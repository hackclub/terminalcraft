"""
Sensor management module for barometric and environmental sensors
Hey, I built this module after a camping trip where I got caught in a sudden storm.
Wish I had pressure data back then to predict it! So now I hook up sensors to avoid surprises.

Note to self: gotta test this with more hardware, only tried on my old Arduino setup so far.
"""

import serial  # for talking to hardware
import json  # saving data to files
import time  # timing stuff
from datetime import datetime, timedelta  # timestamping readings
from typing import Dict, Any, List, Optional  # type hints are handy, tho I forget sometimes
from pathlib import Path  # file handling
import threading  # background monitoring
import logging  # log errors when stuff breaks

from .config import config  # grab settings from config

class SensorManager:
    """Manages sensors for pressure, temp, humidity - basically my weather station brain!"""
    
    def __init__(self):
        # Pull settings from config - I keep changing these based on hardware
        self.sensor_enabled = config.get('sensor.enabled', False)
        self.sensor_port = config.get('sensor.port', '/dev/ttyUSB0')  # default port, might not work for everyone
        self.sensor_baudrate = config.get('sensor.baudrate', 9600)  # standard rate for most sensors I own
        
        # Serial connection placeholder - will set up later if enabled
        self.serial_connection = None
        
        # Default sensor data - I start with average values in case sensor fails
        self.sensor_data = {
            'pressure': {'current': 1013.25, 'history': []},  # standard pressure
            'temperature': {'current': 20.0, 'history': []},  # room temp
            'humidity': {'current': 50.0, 'history': []}  # average humidity
        }
        
        # File to store data - I lost data once during a power outage, never again!
        self.data_file = config.data_dir / "sensor_data.json"
        self.monitoring_thread = None
        self.is_monitoring = False
        
        # Load old data if it exists - super useful after reboots
        self._load_sensor_data()
        
        # If sensor is enabled in config, try to connect
        if self.sensor_enabled:
            print("🔌 Attempting to connect to sensor...")
            self._initialize_sensor()
        else:
            print("[dim]💡 Sensor disabled in config. Use --enable-sensor to activate.[/dim]")
    
    def _load_sensor_data(self):
        """Load historical sensor data from file - I hate losing history!"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    saved_data = json.load(f)
                    self.sensor_data.update(saved_data)
                    print(f"📂 Loaded historical sensor data from {self.data_file}")
            except (json.JSONDecodeError, IOError) as e:
                logging.warning(f"Could not load sensor data: {e}")
                print("[yellow]⚠️ Couldn't load old sensor data, starting fresh.[/yellow]")
    
    def _save_sensor_data(self):
        """Save sensor data to file so I don't lose it on crash"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.sensor_data, f, indent=2, default=str)
        except IOError as e:
            logging.warning(f"Could not save sensor data: {e}")
            print("[red]❌ Error saving sensor data![/red]")
    
    def _initialize_sensor(self):
        """Set up connection to sensor - fingers crossed it works first try!"""
        try:
            self.serial_connection = serial.Serial(
                self.sensor_port,
                self.sensor_baudrate,
                timeout=5  # give it a few secs to respond
            )
            print(f"✅ Connected to sensor on {self.sensor_port} at {self.sensor_baudrate} baud")
            
            # Start a background thread to keep reading data - learned this the hard way
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self._monitor_sensor)
            self.monitoring_thread.daemon = True  # die with main program
            self.monitoring_thread.start()
            print("🌀 Started background sensor monitoring")
            
        except serial.SerialException as e:
            print(f"[red]❌ Warning: Could not connect to sensor: {e}[/red]")
            print("[dim]💡 Check if device is plugged in or use --simulate for testing[/dim]")
            self.sensor_enabled = False
    
    def _monitor_sensor(self):
        """Keep reading sensor data in background - I check this every second like an anxious parent!"""
        while self.is_monitoring and self.serial_connection:
            try:
                # Check if there's data waiting to be read
                if self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    self._parse_sensor_data(line)
                
                time.sleep(1)  # don't hog CPU, check once a second
                
            except Exception as e:
                logging.error(f"Error reading sensor data: {e}")
                print(f"[red]⚠️ Sensor read error: {e}[/red]")
                time.sleep(5)  # wait a bit before retrying, don't spam errors
    
    def _parse_sensor_data(self, data_line: str):
        """Parse the raw data from sensor - took me forever to support both JSON and plain text formats"""
        try:
            # I support two formats because my old sensor used plain text, new one uses JSON
            # Format 1: "PRESSURE:1015.2,TEMP:22.5,HUMIDITY:65.0"
            # Format 2: {"pressure": 1015.2, "temperature": 22.5, "humidity": 65.0}
            
            current_time = datetime.utcnow().isoformat()  # timestamp for history
            
            if data_line.startswith('{'):
                # JSON format - newer sensors use this
                data = json.loads(data_line)
                print(f"📥 Got JSON sensor data: {data_line[:50]}...")
                
                if 'pressure' in data:
                    self._update_sensor_value('pressure', data['pressure'], current_time)
                if 'temperature' in data:
                    self._update_sensor_value('temperature', data['temperature'], current_time)
                if 'humidity' in data:
                    self._update_sensor_value('humidity', data['humidity'], current_time)
            
            else:
                # Old-school comma-separated format - my first sensor used this
                parts = data_line.split(',')
                print(f"📥 Got plain sensor data: {data_line[:50]}...")
                for part in parts:
                    if ':' in part:
                        key, value = part.split(':', 1)
                        key = key.lower().strip()
                        value = float(value.strip())
                        
                        if key in ['pressure', 'press', 'p']:
                            self._update_sensor_value('pressure', value, current_time)
                        elif key in ['temperature', 'temp', 't']:
                            self._update_sensor_value('temperature', value, current_time)
                        elif key in ['humidity', 'humid', 'h']:
                            self._update_sensor_value('humidity', value, current_time)
            
            # Save to file every 60 readings so I don't lose too much if it crashes
            if len(self.sensor_data['pressure']['history']) % 60 == 0:
                print("💾 Saving sensor data to file...")
                self._save_sensor_data()
        
        except (ValueError, json.JSONDecodeError) as e:
            logging.warning(f"Could not parse sensor data '{data_line}': {e}")
            print(f"[yellow]⚠️ Bad sensor data format: {data_line[:30]}...[/yellow]")
    
    def _update_sensor_value(self, sensor_type: str, value: float, timestamp: str):
        """Update sensor readings and keep history - I limit to 24h to save space"""
        if sensor_type not in self.sensor_data:
            return
        
        # Update current value
        self.sensor_data[sensor_type]['current'] = value
        self.sensor_data[sensor_type]['history'].append({
            'value': value,
            'timestamp': timestamp
        })
        
        # Only keep last 24 hours - my disk filled up once with old data!
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.sensor_data[sensor_type]['history'] = [
            h for h in self.sensor_data[sensor_type]['history']
            if datetime.fromisoformat(h['timestamp'].replace('Z', '+00:00')) > cutoff_time
        ]
        # Quick sanity check - sometimes sensors send crazy values
        if sensor_type == 'pressure' and (value < 800 or value > 1200):
            print(f"[yellow]⚠️ Weird pressure value {value}mb - sensor glitch?[/yellow]")
    
    def get_current_readings(self) -> Dict[str, Any]:
        """Return current sensor values - used by other modules"""
        if not self.sensor_enabled:
            print("[dim]💡 Sensors disabled, no readings available[/dim]")
            return {}
        
        return {
            'pressure': {
                'current': self.sensor_data['pressure']['current'],
                'unit': 'mb',
                'timestamp': datetime.utcnow().isoformat()
            },
            'temperature': {
                'current': self.sensor_data['temperature']['current'],
                'unit': '°C',
                'timestamp': datetime.utcnow().isoformat()
            },
            'humidity': {
                'current': self.sensor_data['humidity']['current'],
                'unit': '%',
                'timestamp': datetime.utcnow().isoformat()
            }
        }
    
    def get_pressure_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get pressure history for trend analysis - I use 24h by default"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        history = [
            h for h in self.sensor_data['pressure']['history']
            if datetime.fromisoformat(h['timestamp'].replace('Z', '+00:00')) > cutoff_time
        ]
        print(f"📊 Returning {len(history)} pressure data points for last {hours}h")
        return history
    
    def get_sensor_status(self) -> Dict[str, Any]:
        """Check if sensor is working - handy for debugging"""
        status = {
            'enabled': self.sensor_enabled,
            'connected': self.serial_connection is not None and self.serial_connection.is_open,
            'port': self.sensor_port,
            'baudrate': self.sensor_baudrate,
            'monitoring': self.is_monitoring
        }
        
        if self.sensor_enabled:
            status['last_readings'] = {
                'pressure': {
                    'value': self.sensor_data['pressure']['current'],
                    'time': self.sensor_data['pressure']['history'][-1]['timestamp'] if self.sensor_data['pressure']['history'] else 'N/A'
                },
                'temperature': {
                    'value': self.sensor_data['temperature']['current'],
                    'time': self.sensor_data['temperature']['history'][-1]['timestamp'] if self.sensor_data['temperature']['history'] else 'N/A'
                },
                'humidity': {
                    'value': self.sensor_data['humidity']['current'],
                    'time': self.sensor_data['humidity']['history'][-1]['timestamp'] if self.sensor_data['humidity']['history'] else 'N/A'
                }
            }
        return status
    
    def calibrate_sensor(self, reference_pressure: float):
        """Calibrate pressure sensor against a reference"""
        if not self.sensor_enabled:
            return False
        
        current_reading = self.sensor_data['pressure']['current']
        offset = reference_pressure - current_reading
        
        # Apply calibration offset to future readings
        # This is a simplified calibration - real sensors might need more complex calibration
        self.calibration_offset = offset
        
        print(f"Sensor calibrated. Offset: {offset:.2f} mb")
        return True
    
    def simulate_sensor_data(self, duration_minutes: int = 60):
        """Simulate sensor data for testing purposes"""
        if self.sensor_enabled:
            print("Warning: Real sensor is enabled. Simulation skipped.")
            return
        
        print(f"Simulating sensor data for {duration_minutes} minutes...")
        
        import random
        import numpy as np
        
        # Generate realistic sensor data
        base_pressure = 1013.25
        base_temp = 20.0
        base_humidity = 50.0
        
        current_time = datetime.utcnow()
        
        for i in range(duration_minutes):
            timestamp = (current_time - timedelta(minutes=duration_minutes - i)).isoformat()
            
            # Add some realistic variation
            pressure = base_pressure + random.gauss(0, 2) + np.sin(i * 0.1) * 5
            temperature = base_temp + random.gauss(0, 1) + np.sin(i * 0.05) * 3
            humidity = base_humidity + random.gauss(0, 5) + np.sin(i * 0.08) * 10
            
            # Ensure realistic ranges
            pressure = max(950, min(1050, pressure))
            temperature = max(-10, min(40, temperature))
            humidity = max(0, min(100, humidity))
            
            self._update_sensor_value('pressure', pressure, timestamp)
            self._update_sensor_value('temperature', temperature, timestamp)
            self._update_sensor_value('humidity', humidity, timestamp)
        
        self._save_sensor_data()
        print(f"Generated {duration_minutes} minutes of simulated sensor data")
    
    def close(self):
        """Close sensor connection"""
        self.is_monitoring = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
        
        self._save_sensor_data()

# Global sensor manager instance
sensor_manager = SensorManager()