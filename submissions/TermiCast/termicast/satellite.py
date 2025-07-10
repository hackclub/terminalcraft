"""
Satellite tracking magic - this is where we follow the birds in the sky! 🛰️
Handles TLE data and orbital mechanics so you don't have to.

Fun fact: Satellites move at about 17,500 mph. That's... really fast.
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import numpy as np

from skyfield.api import load, EarthSatellite, wgs84, utc
from skyfield.timelib import Time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable

from .config import config

class SatelliteTracker:
    """The brain behind satellite tracking - orbital mechanics made somewhat simple"""
    
    def __init__(self):
        # Skyfield's timescale - handles all the complicated time stuff
        self.ts = load.timescale()
        self.satellites = {}  # Our satellite database
        
        # Get the list of weather satellites we care about
        self.weather_satellites = config.get('satellites.weather_satellites', [])
        
        # Load up all the satellite data
        self._load_tle_data()
        
        # Keep track of failed geocoding attempts (for debugging)
        self.geocoding_failures = 0
    
    def _load_tle_data(self):
        """Load TLE (Two-Line Element) data - the GPS coordinates for satellites"""
        tle_dir = config.tle_dir
        
        if not tle_dir.exists():
            print(f"🤔 No TLE directory found at {tle_dir}")
            print("   Creating some sample data so things don't break...")
            self._create_sample_tle_data()
        
        # Hunt through all TLE files and load them up
        tle_files = list(tle_dir.glob("*.txt")) + list(tle_dir.glob("*.tle"))
        
        if not tle_files:
            print("⚠️  No TLE files found - creating sample data")
            self._create_sample_tle_data()
            tle_files = list(tle_dir.glob("*.txt"))
        
        loaded_count = 0
        for tle_file in tle_files:
            count = self._parse_tle_file(tle_file)
            loaded_count += count
        
        print(f"📡 Loaded {loaded_count} satellites from {len(tle_files)} TLE files")
    
    def _create_sample_tle_data(self):
        """Create some sample TLE data so the app doesn't crash on first run"""
        config.tle_dir.mkdir(exist_ok=True)
        
        # Real-ish TLE data (simplified for demo purposes)
        # Note: These are not current real TLE data - just for testing!
        sample_tle = """NOAA-19                 
1 33591U 09005A   23001.00000000  .00000000  00000-0  00000-0 0  9990
2 33591  99.1000 100.0000 0010000  90.0000 270.0000 14.12000000000000
NOAA-18                 
1 28654U 05018A   23001.00000000  .00000000  00000-0  00000-0 0  9991
2 28654  99.0500  95.0000 0012000  85.0000 275.0000 14.11500000000000
METOP-A                 
1 29499U 06044A   23001.00000000  .00000000  00000-0  00000-0 0  9992
2 29499  98.7000 102.0000 0001000  88.0000 272.0000 14.21000000000000
NOAA-20
1 43013U 17073A   23001.00000000  .00000000  00000-0  00000-0 0  9993
2 43013  98.7200  98.0000 0001200  92.0000 268.0000 14.19500000000000"""
        
        sample_file = config.tle_dir / "weather_satellites.txt"
        with open(sample_file, 'w') as f:
            f.write(sample_tle)
    
        print(f"📄 Created sample TLE file: {sample_file}")
        print("   💡 Tip: Download real TLE data from celestrak.com for better accuracy!")
    
    def _parse_tle_file(self, tle_file: Path) -> int:
        """Parse a TLE file and extract satellite data - TLE format is weird but standard"""
        satellites_loaded = 0
        
        try:
            with open(tle_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            
            # TLE format: every 3 lines = 1 satellite (name, line1, line2)
            for i in range(0, len(lines), 3):
                if i + 2 < len(lines):
                    name = lines[i]
                    line1 = lines[i + 1]
                    line2 = lines[i + 2]
                    
                    # Validate that this looks like TLE data
                    if not (line1.startswith('1 ') and line2.startswith('2 ')):
                        continue  # Skip invalid entries
                    
                    try:
                        # Create satellite object - skyfield does the heavy lifting
                        satellite = EarthSatellite(line1, line2, name, self.ts)
                        self.satellites[name] = satellite
                        satellites_loaded += 1
                        
                    except Exception as e:
                        print(f"⚠️  Couldn't parse satellite {name}: {e}")
        
        except (IOError, UnicodeDecodeError) as e:
            print(f"❌ Couldn't read TLE file {tle_file}: {e}")
        
        return satellites_loaded
    
    def get_location_coordinates(self, location: str) -> Tuple[float, float]:
        """Turn a place name into lat/lon coordinates - geography made digital"""
        try:
            # Use OpenStreetMap's geocoding service (free and no API key needed!)
            geolocator = Nominatim(user_agent="termicast-weather-app")
            location_data = geolocator.geocode(location, timeout=10)
            
            if location_data:
                lat, lon = location_data.latitude, location_data.longitude
                print(f"📍 Found {location} at {lat:.2f}°, {lon:.2f}°")
                return lat, lon
            else:
                raise ValueError(f"Location '{location}' not found in geocoding database")
                
        except (GeocoderUnavailable, Exception) as e:
            # Geocoding failed - fall back to default location
            self.geocoding_failures += 1
            default_loc = config.get('default_location')
            
            print(f"🗺️  Geocoding failed for '{location}': {e}")
            print(f"   Using default location: {default_loc['name']}")
            
            return default_loc['latitude'], default_loc['longitude']
    
    def predict_passes(self, location: str, start_time: Optional[datetime] = None, 
                      duration_hours: int = 24) -> List[Dict[str, Any]]:
        """The main event - predict when satellites will be visible from your location"""
        
        # Default to now if no start time given
        if start_time is None:
            start_time = datetime.utcnow().replace(tzinfo=utc)
        elif start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=utc)
        
        end_time = start_time + timedelta(hours=duration_hours)
        
        print(f"🔮 Predicting satellite passes from {start_time.strftime('%Y-%m-%d %H:%M')} UTC")
        print(f"   Duration: {duration_hours} hours")
        
        # Get observer location
        lat, lon = self.get_location_coordinates(location)
        observer = wgs84.latlon(lat, lon)
        
        passes = []
        satellites_checked = 0
        
        for sat_name, satellite in self.satellites.items():
            # Only check weather satellites (ignore other random satellites)
            if sat_name in self.weather_satellites:
                satellites_checked += 1
                try:
                    # Calculate satellite positions at regular intervals
                    # 5-minute intervals gives good resolution without being too slow
                    time_samples = []
                    for minutes in range(0, duration_hours * 60, 5):
                        sample_time = start_time + timedelta(minutes=minutes)
                        if sample_time.tzinfo is None:
                            sample_time = sample_time.replace(tzinfo=utc)
                        time_samples.append(sample_time)
                    
                    times = self.ts.utc([t for t in time_samples])
                    
                    # Get satellite positions in space
                    geocentric = satellite.at(times)
                    subpoint = wgs84.subpoint(geocentric)
                    
                    # Calculate what the observer would see (elevation, azimuth, distance)
                    difference = satellite - observer
                    topocentric = difference.at(times)
                    elevation, azimuth, distance = topocentric.altaz()
                    
                    # Filter for visible passes (above minimum elevation)
                    min_elevation = config.get('prediction.min_elevation', 10.0)
                    
                    for i, elev in enumerate(elevation.degrees):
                        if elev > min_elevation:
                            pass_time = times[i].utc_datetime()
                            if pass_time.tzinfo is None:
                                pass_time = pass_time.replace(tzinfo=utc)
                            
                            # Record this pass
                            passes.append({
                                'satellite': sat_name,
                                'time': pass_time,
                                'elevation': round(elev, 1),
                                'azimuth': round(azimuth.degrees[i], 1),
                                'distance': round(distance.km[i]),
                                'latitude': round(subpoint.latitude.degrees[i], 2),
                                'longitude': round(subpoint.longitude.degrees[i], 2),
                                'type': self._classify_satellite_type(sat_name),
                                'quality': 'excellent' if elev > 60 else 'good' if elev > 30 else 'fair'
                            })
                
                except Exception as e:
                    print(f"⚠️  Couldn't calculate passes for {sat_name}: {e}")
        
        # Sort chronologically and remove duplicates that are too close together
        passes.sort(key=lambda x: x['time'])
        passes = self._deduplicate_close_passes(passes)
        
        print(f"✅ Found {len(passes)} visible passes from {satellites_checked} satellites")
        return passes
    
    def _deduplicate_close_passes(self, passes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove passes that are too close together in time (avoids spam)"""
        if not passes:
            return passes
        
        deduplicated = [passes[0]]  # Always keep the first pass
        
        for current_pass in passes[1:]:
            last_pass = deduplicated[-1]
            
            # If same satellite and passes are less than 10 minutes apart, skip
            if (current_pass['satellite'] == last_pass['satellite'] and
                abs((current_pass['time'] - last_pass['time']).total_seconds()) < 600):
                continue
            
            deduplicated.append(current_pass)
        
        return deduplicated
    
    def _classify_satellite_type(self, sat_name: str) -> str:
        """Figure out what kind of satellite this is based on its name"""
        name_upper = sat_name.upper()
        
        if 'NOAA' in name_upper:
            return 'Polar Weather'
        elif 'METOP' in name_upper:
            return 'European Weather'
        elif 'GOES' in name_upper:
            return 'Geostationary Weather'
        elif 'AQUA' in name_upper or 'TERRA' in name_upper:
            return 'Earth Observation'
        else:
            return 'Weather Satellite'  # Generic fallback
    
    def get_current_satellite_positions(self) -> List[Dict[str, Any]]:
        """Where are all our satellites right now?"""
        current_time = self.ts.now()
        positions = []
        
        for sat_name, satellite in self.satellites.items():
            if sat_name in self.weather_satellites:
                try:
                    # Get current position
                    geocentric = satellite.at(current_time)
                    subpoint = wgs84.subpoint(geocentric)
                    
                    positions.append({
                        'satellite': sat_name,
                        'latitude': round(subpoint.latitude.degrees, 2),
                        'longitude': round(subpoint.longitude.degrees, 2),
                        'altitude': round(subpoint.elevation.km, 1),
                        'type': self._classify_satellite_type(sat_name),
                        'hemisphere': 'Northern' if subpoint.latitude.degrees > 0 else 'Southern'
                    })
                
                except Exception as e:
                    print(f"⚠️  Couldn't get position for {sat_name}: {e}")
        
        # Sort by latitude (north to south)
        positions.sort(key=lambda x: x['latitude'], reverse=True)
        return positions
    
    def get_satellite_info(self, sat_name: str) -> Dict[str, Any]:
        """Get detailed information about a satellite"""
        if sat_name not in self.satellites:
            return {}
        
        satellite = self.satellites[sat_name]
        current_time = self.ts.now()
        
        try:
            geocentric = satellite.at(current_time)
            subpoint = wgs84.subpoint(geocentric)
            
            return {
                'name': sat_name,
                'latitude': subpoint.latitude.degrees,
                'longitude': subpoint.longitude.degrees,
                'altitude': subpoint.elevation.km,
                'type': self._classify_satellite_type(sat_name),
                'epoch': satellite.epoch.utc_datetime(),
                'period_minutes': 24 * 60 / satellite.model.no_kozai * 60,  # Rough orbital period
            }
        
        except Exception as e:
            return {'name': sat_name, 'error': str(e)}

# Global satellite tracker instance
satellite_tracker = SatelliteTracker() 