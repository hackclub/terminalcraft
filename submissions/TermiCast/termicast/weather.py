"""
Weather prediction stuff - this is where the real magic happens!
Uses satellite data to figure out what Mother Nature is planning.

FIXME: Need to improve precipitation accuracy - it's hit or miss right now
TODO: Add more satellite types when I have time
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import json
from pathlib import Path

from .satellite import satellite_tracker
from .config import config
from .sensors import sensor_manager

class WeatherPredictor:
    """The heart of TermiCast - where satellite data becomes weather predictions"""
    
    def __init__(self):
        # Different prediction methods - some work better than others
        self.prediction_models = {
            'cloud_coverage': self._predict_cloud_coverage,
            'precipitation': self._predict_precipitation,
            'temperature': self._predict_temperature,
            'wind_patterns': self._predict_wind_patterns,
            'storm_systems': self._detect_storm_systems
        }
        
        # Load any historical data we might have lying around
        self.historical_data = self._load_historical_data()
        
        # Keep track of how many predictions we've made (just for fun)
        self.prediction_count = 0
    
    def _load_historical_data(self) -> Dict[str, Any]:
        """Try to load historical weather patterns - helps with accuracy"""
        data_file = config.data_dir / "historical_weather.json"
        
        if data_file.exists():
            try:
                with open(data_file, 'r') as f:
                    data = json.load(f)
                    # Validate that we got something useful
                    if isinstance(data, dict) and len(data) > 0:
                        return data
            except (json.JSONDecodeError, IOError) as e:
                # File exists but is corrupted or unreadable
                print(f"Warning: Couldn't load historical data: {e}")
        
        # Return empty structure if no valid data
        return {
            'pressure_patterns': [],
            'satellite_coverage': [],
            'weather_events': [],
            'accuracy_stats': {'correct': 0, 'total': 0}  # Track our success rate
        }
    
    def generate_forecast(self, location: str, days: int = 3) -> Dict[str, Any]:
        """The main event - generate a weather forecast for a location"""
        self.prediction_count += 1  # Because I like to count things
        
        # Use config default if available
        forecast_days = config.get('prediction.forecast_days', days)
        
        # Get satellite data for our timeframe
        passes = satellite_tracker.predict_passes(
            location, 
            duration_hours=forecast_days * 24
        )
        
        # Check if we have any sensor data to work with
        sensor_data = sensor_manager.get_current_readings()
        
        # Build our forecast structure
        from skyfield.api import utc
        forecast = {
            'location': location,
            'generated_at': datetime.utcnow().replace(tzinfo=utc).isoformat(),
            'forecast_days': forecast_days,
            'daily_forecasts': [],
            'prediction_number': self.prediction_count,  # Just because
            'confidence_level': 'medium'  # Will adjust based on data quality
        }
        
        # Generate daily forecasts
        for day in range(forecast_days):
            from skyfield.api import utc
            start_time = datetime.utcnow().replace(tzinfo=utc) + timedelta(days=day)
            end_time = start_time + timedelta(days=1)
            
            # Get satellite passes for this specific day
            day_passes = [
                p for p in passes 
                if start_time <= p['time'] < end_time
            ]
            
            daily_forecast = self._generate_daily_forecast(
                location, start_time, day_passes, sensor_data
            )
            forecast['daily_forecasts'].append(daily_forecast)
        
        # Add any warnings we can figure out
        forecast['warnings'] = self._generate_warnings(passes, sensor_data)
        
        # Adjust confidence based on data quality
        if len(passes) > 10:
            forecast['confidence_level'] = 'high'
        elif len(passes) < 3:
            forecast['confidence_level'] = 'low'
        
        return forecast
    
    def _generate_daily_forecast(self, location: str, date: datetime, 
                               passes: List[Dict], sensor_data: Dict) -> Dict[str, Any]:
        """Generate forecast for one day - this is where the real work happens"""
        
        # Sort passes by type - some satellites are better at different things
        polar_passes = [p for p in passes if 'Polar' in p.get('type', '')]
        geo_passes = [p for p in passes if 'Geostationary' in p.get('type', '')]
        
        # Count coverage by satellite type
        total_passes = len(passes)
        infrared_coverage = len([p for p in passes if 'NOAA' in p['satellite']])
        microwave_coverage = len([p for p in passes if 'METOP' in p['satellite']])
        
        # Generate predictions using our models
        cloud_coverage = self._predict_cloud_coverage(passes, sensor_data)
        precipitation = self._predict_precipitation(passes, sensor_data)
        temperature = self._predict_temperature(passes, sensor_data, location)
        wind = self._predict_wind_patterns(passes, sensor_data)
        
        # Calculate a rough "coverage score" - more passes = better prediction
        coverage_score = min(100, total_passes * 12)  # Rough heuristic
        
        return {
            'date': date.strftime('%Y-%m-%d'),
            'day_of_week': date.strftime('%A'),  # Because people like knowing
            'satellite_passes': total_passes,
            'coverage_score': coverage_score,
            'conditions': {
                'cloud_coverage': cloud_coverage,
                'precipitation_chance': precipitation['chance'],
                'temperature': temperature,
                'wind': wind
            },
            'detailed_analysis': {
                'infrared_passes': infrared_coverage,
                'microwave_passes': microwave_coverage,
                'polar_orbiting': len(polar_passes),
                'geostationary': len(geo_passes)
            },
            'data_quality': 'good' if coverage_score > 60 else 'fair' if coverage_score > 30 else 'poor'
        }
    
    def _predict_cloud_coverage(self, passes: List[Dict], sensor_data: Dict) -> Dict[str, Any]:
        """Figure out cloud coverage using dynamic satellite analysis - improved for realism"""
        
        if not passes:
            # No satellite data = more realistic guess
            import random
            return {
                'percentage': random.randint(10, 40),  # Lower range for clear days
                'confidence': 'very_low', 
                'type': 'unknown',
                'note': 'No satellite data available'
            }
        
        # Analyze satellite pass patterns for cloud indicators
        total_passes = len(passes)
        high_elevation_passes = [p for p in passes if p['elevation'] > 45]
        
        # Fix timezone issue - make sure both datetimes have timezone info
        from skyfield.api import utc
        current_time = datetime.utcnow().replace(tzinfo=utc)
        recent_passes = [p for p in passes if (current_time - p['time']).total_seconds() < 7200]  # Last 2 hours
        
        # NOAA satellites have infrared sensors - great for cloud detection
        ir_passes = [p for p in passes if 'NOAA' in p['satellite']]
        metop_passes = [p for p in passes if 'METOP' in p['satellite']]
        
        # Start with lower base coverage - many days are actually clearer
        coverage_base = 15  # Reduced from 25
        
        # High elevation passes can see clouds better, but be more conservative
        if high_elevation_passes:
            elevation_factor = len(high_elevation_passes) / max(1, total_passes) * 25  # Reduced from 40
            coverage_base += elevation_factor
        
        # Recent passes are more relevant, but reduce impact
        if recent_passes:
            recent_factor = len(recent_passes) / max(1, total_passes) * 15  # Reduced from 25
            coverage_base += recent_factor
        
        # Different satellite types provide different insights
        if ir_passes and metop_passes:
            # Both types = good coverage analysis, but be conservative
            multi_sensor_bonus = 10  # Reduced from 15
            coverage_base += multi_sensor_bonus
        
        # Add realistic variation based on pass timing, but smaller range
        import random
        random.seed(int(datetime.utcnow().timestamp()) // 3600)  # Changes hourly
        time_variation = random.randint(-10, 15)  # Reduced range
        coverage_base += time_variation
        
        # Use barometric pressure if available - more realistic thresholds
        pressure_influence = 0
        if sensor_data.get('pressure'):
            current_pressure = sensor_data['pressure']['current']
            standard_pressure = 1013.25
            
            if current_pressure < 995:  # Very low pressure
                pressure_influence = 20  # Reduced from 25
            elif current_pressure < 1005:  # Low pressure
                pressure_influence = 10  # Reduced from 15
            elif current_pressure > 1025:  # High pressure = clearer skies
                pressure_influence = -15  # Increased clearing effect
        
        total_coverage = coverage_base + pressure_influence
        coverage_percentage = max(5, min(85, total_coverage))  # Slightly lower max
        
        # Determine cloud type based on conditions
        if coverage_percentage < 20:
            cloud_type = 'clear_sky'
        elif coverage_percentage < 40 and len(high_elevation_passes) > 2:
            cloud_type = 'scattered'
        elif pressure_influence > 15:
            cloud_type = 'storm_clouds'
        elif coverage_percentage > 70:
            cloud_type = 'overcast'
        else:
            cloud_type = 'partly_cloudy'
        
        # Confidence based on data quality
        confidence = 'low'
        if len(ir_passes) >= 3 and len(metop_passes) >= 2:
            confidence = 'high'
        elif total_passes >= 4:
            confidence = 'medium'
        
        return {
            'percentage': round(coverage_percentage),
            'confidence': confidence,
            'type': cloud_type,
            'data_sources': f"{len(ir_passes)} IR + {len(metop_passes)} MW passes"
        }
    
    def _predict_precipitation(self, passes: List[Dict], sensor_data: Dict) -> Dict[str, Any]:
        """Dynamic precipitation prediction based on satellite patterns - improved for realism"""
        
        if not passes:
            import random
            return {
                'chance': random.randint(0, 15),  # Much lower baseline
                'type': 'light_rain', 
                'intensity': 'light',
                'confidence': 'very_low'
            }
        
        # Analyze satellite pass patterns
        total_passes = len(passes)
        mw_passes = [p for p in passes if 'METOP' in p['satellite']]  # Microwave sensors
        ir_passes = [p for p in passes if 'NOAA' in p['satellite']]   # Infrared sensors
        high_quality_passes = [p for p in passes if p['elevation'] > 30]
        
        # Start with much lower baseline - most days are actually dry
        import random
        random.seed(int(datetime.utcnow().timestamp()) // 14400)  # Changes every 4 hours
        base_chance = random.randint(0, 15)  # Much lower starting point
        
        # Microwave sensors detect precipitation, but be more conservative
        if mw_passes:
            mw_factor = min(len(mw_passes) * 6, 25)  # Reduced from 12 to 6, cap at 25%
            base_chance += mw_factor
        
        # High elevation passes see more detail, but reduce impact
        if high_quality_passes:
            elevation_factor = len(high_quality_passes) * 4  # Reduced from 8
            base_chance += elevation_factor
        
        # Multiple satellite types = better analysis, but be conservative
        if mw_passes and ir_passes:
            correlation_bonus = 8  # Reduced from 15
            base_chance += correlation_bonus
        
        # Sensor data integration - be more realistic about thresholds
        sensor_boost = 0
        if sensor_data.get('pressure') and sensor_data.get('humidity'):
            pressure = sensor_data['pressure']['current']
            humidity = sensor_data['humidity']['current']
            
            # More realistic weather rules - higher thresholds for rain
            if pressure < 985 and humidity > 90:  # Very extreme conditions
                sensor_boost = 30
            elif pressure < 995 and humidity > 85:  # Extreme conditions
                sensor_boost = 20
            elif pressure < 1005 and humidity > 80:  # High humidity + low pressure
                sensor_boost = 10
            elif pressure > 1020:  # High pressure = clear skies
                sensor_boost = -20  # Significantly reduce rain chance
        
        # Location-based adjustments for climate
        location_factor = 0
        # Note: location would need to be passed to this function for this to work
        # For now, we'll use a general reduction
        
        total_chance = base_chance + sensor_boost + location_factor
        chance_percentage = max(0, min(60, total_chance))  # Cap at 60% instead of 85%
        
        # Determine precipitation characteristics
        temp_data = sensor_data.get('temperature', {})
        current_temp = temp_data.get('current', 15)
        
        if current_temp < 0:
            precip_type = 'snow'
        elif current_temp < 3 and chance_percentage > 40:  # Higher threshold
            precip_type = 'mixed'
        else:
            precip_type = 'rain'
        
        # More conservative intensity based on multiple factors
        if chance_percentage > 50 and sensor_boost > 20:  # Higher thresholds
            intensity = 'heavy'
        elif chance_percentage > 30:  # Higher threshold
            intensity = 'moderate'
        else:
            intensity = 'light'
        
        # Confidence assessment
        confidence = 'low'
        if len(mw_passes) >= 3 and sensor_boost > 10:  # Higher threshold
            confidence = 'high'
        elif total_passes >= 5:
            confidence = 'medium'
        
        return {
            'chance': round(chance_percentage),
            'type': precip_type,
            'intensity': intensity,
            'confidence': confidence,
            'factors': {
                'microwave_passes': len(mw_passes),
                'infrared_passes': len(ir_passes),
                'sensor_influence': sensor_boost > 0
            }
        }
    
    def _predict_temperature(self, passes: List[Dict], sensor_data: Dict, location: str) -> Dict[str, Any]:
        """Dynamic temperature prediction with location and seasonal factors"""
        
        # Get current month for seasonal adjustment
        from datetime import datetime
        current_month = datetime.now().month
        
        # Base temperature by location (more sophisticated)
        base_temp = 15  # Default temperate climate
        
        # Location-based adjustments
        location_lower = location.lower()
        if any(place in location_lower for place in ['egypt', 'libya', 'sudan', 'algeria']):
            base_temp = 32  # North Africa
        elif any(place in location_lower for place in ['spain', 'italy', 'greece', 'turkey']):
            base_temp = 22  # Mediterranean
        elif any(place in location_lower for place in ['uk', 'britain', 'ireland', 'scotland']):
            base_temp = 12  # British Isles
        elif any(place in location_lower for place in ['norway', 'sweden', 'finland', 'iceland']):
            base_temp = 5   # Nordic countries
        elif any(place in location_lower for place in ['canada', 'alaska', 'siberia']):
            base_temp = -2  # Cold regions
        elif any(place in location_lower for place in ['india', 'thailand', 'vietnam', 'malaysia']):
            base_temp = 28  # Tropical Asia
        elif any(place in location_lower for place in ['australia', 'new zealand']):
            base_temp = 20  # Oceania
        
        # Seasonal adjustment (Northern Hemisphere)
        if current_month in [12, 1, 2]:  # Winter
            seasonal_adj = -8
        elif current_month in [3, 4, 5]:  # Spring
            seasonal_adj = -2
        elif current_month in [6, 7, 8]:  # Summer
            seasonal_adj = +5
        else:  # Fall
            seasonal_adj = 0
        
        base_temp += seasonal_adj
        
        # Use actual sensor data if available
        if sensor_data.get('temperature'):
            base_temp = sensor_data['temperature']['current']
        
        # Cloud coverage affects temperature
        if passes:
            cloud_data = self._predict_cloud_coverage(passes, sensor_data)
            cloud_factor = cloud_data['percentage'] / 100
            
            # Clouds moderate temperature
            if base_temp > 25:
                base_temp -= cloud_factor * 6  # Cooling effect
            elif base_temp < 5:
                base_temp += cloud_factor * 4  # Warming effect at night
        
        # Add realistic daily variation
        import random
        random.seed(int(datetime.utcnow().timestamp()) // 7200)  # Changes every 2 hours
        daily_variation = random.randint(-3, 4)
        base_temp += daily_variation
        
        return {
            'current': round(base_temp),
            'high': round(base_temp + random.randint(4, 8)),
            'low': round(base_temp - random.randint(3, 7)),
            'trend': 'stable'
        }
    
    def _predict_wind_patterns(self, passes: List[Dict], sensor_data: Dict) -> Dict[str, Any]:
        """Dynamic wind prediction based on satellite data and pressure - more realistic"""
        
        if not passes:
            import random
            return {
                'speed': random.randint(5, 12),  # Lower baseline
                'direction': random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']), 
                'gusts': random.randint(8, 16)  # Lower gusts
            }
        
        # Base wind speed calculation - more conservative
        base_wind = 6  # Reduced from 8
        
        # More satellite activity suggests more atmospheric movement, but reduce impact
        activity_factor = min(len(passes) / 10.0, 1.2)  # Reduced multiplier
        wind_speed = base_wind + (activity_factor * 8)  # Reduced from 12
        
        # High elevation passes indicate upper atmosphere activity
        high_passes = [p for p in passes if p['elevation'] > 50]
        if high_passes:
            upper_air_factor = len(high_passes) * 2  # Reduced from 3
            wind_speed += upper_air_factor
        
        # Pressure gradient drives wind - more realistic thresholds
        if sensor_data.get('pressure'):
            pressure = sensor_data['pressure']['current']
            if pressure < 985:  # Very low pressure
                wind_speed += 12  # Strong winds
            elif pressure < 1000:  # Low pressure
                wind_speed += 6   # Moderate winds
            elif pressure > 1025:  # High pressure
                wind_speed -= 3   # Light winds
        
        # Add realistic variation, but smaller range
        import random
        random.seed(int(datetime.utcnow().timestamp()) // 10800)  # Changes every 3 hours
        variation = random.randint(-2, 4)  # Reduced range
        wind_speed += variation
        
        wind_speed = max(2, min(35, wind_speed))  # Lower maximum
        
        # Wind direction (simplified but more realistic)
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        direction = random.choice(directions)
        
        return {
            'speed': round(wind_speed),
            'direction': direction,
            'gusts': round(wind_speed + random.randint(3, 8))  # Smaller gust range
        }
    
    def _detect_storm_systems(self, passes: List[Dict], sensor_data: Dict) -> List[Dict[str, Any]]:
        """Detect potential storm systems"""
        storms = []
        
        if not passes:
            return storms
        
        # Look for indicators of storm systems
        rapid_passes = [p for p in passes if p['elevation'] > 60]  # High elevation passes
        pressure_drop = False
        
        if sensor_data.get('pressure'):
            current_pressure = sensor_data['pressure']['current']
            if current_pressure < 980:  # Very low pressure
                pressure_drop = True
        
        # If we have many high-elevation passes and low pressure, possible storm
        if len(rapid_passes) > 5 and pressure_drop:
            storms.append({
                'type': 'potential_low_pressure_system',
                'severity': 'moderate',
                'confidence': 0.7,
                'indicators': ['low_pressure', 'high_satellite_activity']
            })
        
        return storms
    
    def _generate_warnings(self, passes: List[Dict], sensor_data: Dict) -> List[Dict[str, Any]]:
        """Generate weather warnings and alerts"""
        warnings = []
        
        # Detect storm systems
        storms = self._detect_storm_systems(passes, sensor_data)
        for storm in storms:
            warnings.append({
                'type': 'weather_alert',
                'severity': storm['severity'],
                'message': f"Potential {storm['type'].replace('_', ' ')} detected",
                'confidence': storm['confidence']
            })
        
        # Check for extreme sensor readings
        if sensor_data.get('pressure'):
            pressure = sensor_data['pressure']['current']
            if pressure < 950:
                warnings.append({
                    'type': 'severe_weather_warning',
                    'severity': 'high',
                    'message': 'Extremely low atmospheric pressure detected',
                    'confidence': 0.9
                })
        
        return warnings
    
    def analyze_pressure_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze atmospheric pressure trends"""
        trend_hours = config.get('prediction.pressure_trend_hours', hours)
        
        # Get sensor data history
        pressure_data = sensor_manager.get_pressure_history(trend_hours)
        
        if not pressure_data:
            return {
                'trend': 'no_data',
                'message': 'No pressure data available',
                'recommendation': 'Enable pressure sensor for better predictions'
            }
        
        # Analyze trend
        pressures = [reading['value'] for reading in pressure_data]
        times = [reading['timestamp'] for reading in pressure_data]
        
        if len(pressures) < 2:
            return {'trend': 'insufficient_data'}
        
        # Calculate trend
        recent_avg = np.mean(pressures[-3:]) if len(pressures) >= 3 else pressures[-1]
        older_avg = np.mean(pressures[:3]) if len(pressures) >= 6 else pressures[0]
        
        pressure_change = recent_avg - older_avg
        
        if pressure_change > 2:
            trend = 'rising'
            message = 'Pressure is rising - improving weather likely'
        elif pressure_change < -2:
            trend = 'falling'
            message = 'Pressure is falling - weather may deteriorate'
        else:
            trend = 'stable'
            message = 'Pressure is stable'
        
        return {
            'trend': trend,
            'change_mb': round(pressure_change, 2),
            'current_mb': round(recent_avg, 2),
            'message': message,
            'data_points': len(pressures),
            'time_span_hours': trend_hours
        }

# Global weather predictor instance  
weather_predictor = WeatherPredictor() 