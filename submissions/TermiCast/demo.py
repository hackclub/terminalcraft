#!/usr/bin/env python3
"""
TermiCast Demo Script
Demonstrates the main functionality of TermiCast without requiring installation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from termicast.satellite import satellite_tracker
from termicast.weather import weather_predictor
from termicast.sensors import sensor_manager
from termicast.visualization import visualizer
from termicast.config import config

def demo_forecast():
    """Demo weather forecast functionality"""
    print("🌤️  TermiCast Weather Forecast Demo")
    print("=" * 50)
    
    location = "Alexandria, Egypt"
    print(f"Generating forecast for: {location}")
    
    try:
        # Generate forecast
        forecast_data = weather_predictor.generate_forecast(location, 3)
        
        # Display using visualizer
        visualizer.display_forecast(forecast_data)
        
    except Exception as e:
        print(f"Error in forecast demo: {e}")
        import traceback
        traceback.print_exc()

def demo_satellites():
    """Demo satellite tracking functionality"""
    print("\n🛰️  TermiCast Satellite Tracking Demo")
    print("=" * 50)
    
    location = "Alexandria, Egypt"
    print(f"Calculating satellite passes for: {location}")
    
    try:
        # Get satellite passes
        passes = satellite_tracker.predict_passes(location, duration_hours=24)
        
        # Display passes
        visualizer.display_satellite_passes(passes, "Demo - Next 24 Hours")
        
        # Show current positions
        print("\nCurrent Satellite Positions:")
        current_sats = satellite_tracker.get_current_satellite_positions()
        visualizer.display_satellite_status(current_sats)
        
    except Exception as e:
        print(f"Error in satellite demo: {e}")
        import traceback
        traceback.print_exc()

def demo_pressure_trend():
    """Demo pressure trend analysis"""
    print("\n📊 TermiCast Pressure Trend Demo")
    print("=" * 50)
    
    # Generate some simulated sensor data first
    print("Generating simulated sensor data...")
    sensor_manager.simulate_sensor_data(60)  # 60 minutes of data
    
    try:
        # Analyze pressure trends
        trend_data = weather_predictor.analyze_pressure_trends(24)
        
        # Display trend
        visualizer.display_pressure_trend(trend_data)
        
        # Show sensor status
        sensor_status = sensor_manager.get_sensor_status()
        visualizer.display_sensor_status(sensor_status)
        
    except Exception as e:
        print(f"Error in pressure trend demo: {e}")
        import traceback
        traceback.print_exc()

def demo_weather_map():
    """Demo ASCII weather map"""
    print("\n🗺️  TermiCast Weather Map Demo")
    print("=" * 50)
    
    location = "Alexandria, Egypt"
    
    try:
        # Generate forecast for map
        forecast_data = weather_predictor.generate_forecast(location, 1)
        
        # Display weather map
        visualizer.display_ascii_weather_map(location, forecast_data)
        
    except Exception as e:
        print(f"Error in weather map demo: {e}")
        import traceback
        traceback.print_exc()

def demo_system_status():
    """Demo system status display"""
    print("\n🔧 TermiCast System Status Demo")
    print("=" * 50)
    
    try:
        # Show satellite system info
        total_satellites = len(satellite_tracker.satellites)
        weather_satellites = len(satellite_tracker.weather_satellites)
        
        print(f"Loaded Satellites: {total_satellites}")
        print(f"Weather Satellites: {weather_satellites}")
        print(f"TLE Directory: {config.tle_dir}")
        print(f"Data Directory: {config.data_dir}")
        
        # Show configuration
        print("\nConfiguration:")
        default_loc = config.get('default_location')
        print(f"Default Location: {default_loc['name']}")
        print(f"Forecast Days: {config.get('prediction.forecast_days')}")
        print(f"Min Elevation: {config.get('prediction.min_elevation')}°")
        
    except Exception as e:
        print(f"Error in system status demo: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all demo functions"""
    print("🚀 Welcome to TermiCast Demo!")
    print("This demonstrates TermiCast's offline weather forecasting capabilities")
    print("using satellite TLE data and optional sensor integration.\n")
    
    try:
        # Run all demos
        demo_system_status()
        demo_forecast()
        demo_satellites()
        demo_weather_map()
        demo_pressure_trend()
        
        print("\n✅ TermiCast Demo Complete!")
        print("\nTo use TermiCast:")
        print("1. Install: pip install -e .")
        print("2. Run: termicast forecast --location \"Your City\"")
        print("3. Or: termicast satellites --today")
        print("4. Or: termicast map")
        print("5. Or: termicast pressure-trend")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 