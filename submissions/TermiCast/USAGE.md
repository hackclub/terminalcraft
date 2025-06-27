# TermiCast Usage Guide

## Overview

TermiCast is a sophisticated terminal-based weather forecasting application that uses TLE (Two-Line Element Set) satellite data to provide offline weather predictions and natural disaster early warnings.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install TermiCast
pip install -e .
```

## Command Overview

```bash
termicast --help    # Show all available commands
```

### Available Commands:

- `forecast` - Generate weather forecast for a location
- `satellites` - List upcoming satellite passes
- `map` - Display ASCII weather map
- `pressure-trend` - Show atmospheric pressure trends
- `sensor` - Configure barometric sensors
- `status` - Show system status
- `config-cmd` - Configure settings
- `update` - Update satellite data

## Detailed Command Usage

### 1. Weather Forecast

Generate comprehensive weather forecasts using satellite pass analysis:

```bash
# Basic forecast for default location
termicast forecast

# Forecast for specific location
termicast forecast --location "Alexandria, Egypt"

# Multi-day forecast
termicast forecast --location "New York, NY" --days 5
```

**Features:**
- Temperature predictions with high/low ranges
- Cloud coverage percentage and types
- Precipitation probability and intensity
- Wind speed and direction
- Satellite coverage quality score
- Weather warnings and alerts

### 2. Satellite Tracking

Track weather satellites and predict their passes over your location:

```bash
# Today's satellite passes
termicast satellites --today

# Satellite passes for specific location
termicast satellites --location "London, UK"

# Extended prediction window
termicast satellites --hours 48 --location "Tokyo, Japan"
```

**Output includes:**
- Pass times (UTC)
- Satellite names and types
- Elevation angles (higher = better coverage)
- Azimuth directions
- Distance from observer
- Color-coded by elevation quality

### 3. ASCII Weather Map

Visual weather representation using ASCII characters:

```bash
# Generate weather map for location
termicast map --location "Cairo, Egypt"
```

**Features:**
- 8x8 grid weather visualization
- Weather symbol legend
- Current conditions summary
- Real-time satellite positions

### 4. Pressure Trend Analysis

Analyze atmospheric pressure trends for weather prediction:

```bash
# 24-hour pressure analysis (default)
termicast pressure-trend

# Custom time window
termicast pressure-trend --hours 12
```

**Analysis includes:**
- Current pressure reading
- Trend direction (rising/falling/stable)
- Pressure change over time
- Weather implications
- Data quality metrics

### 5. Sensor Management

Configure and test barometric sensors:

```bash
# Show sensor status
termicast sensor

# Configure sensor port
termicast sensor --port /dev/ttyUSB0

# Enable sensor
termicast sensor --enable

# Disable sensor
termicast sensor --disable
```

**Sensor features:**
- USB/GPIO sensor support
- Real-time data collection
- Historical data storage
- Simulated data for testing

### 6. System Status

View comprehensive system information:

```bash
# General system status
termicast status

# Specific satellite information
termicast status --satellite "NOAA-19"
```

**Status includes:**
- Loaded satellites count
- Real-time satellite positions
- Sensor connection status
- Configuration summary

### 7. Configuration

Customize TermiCast settings:

```bash
# View current configuration
termicast config-cmd

# Set default location
termicast config-cmd --location "Paris, France"

# Configure forecast parameters
termicast config-cmd --forecast-days 7 --min-elevation 15.0
```

## Data Management

### TLE Data

TermiCast uses TLE files for satellite tracking:

- **Location**: `tle/` directory
- **Format**: Standard 3-line TLE format
- **Sources**: 
  - https://celestrak.com/NORAD/elements/weather.txt
  - https://celestrak.com/NORAD/elements/resource.txt

**Update TLE data:**
```bash
termicast update --update-tle  # Shows update instructions
```

### Historical Data

Weather patterns and sensor data stored in:
- **Configuration**: `~/.termicast/config.json`
- **Sensor data**: `data/sensor_data.json`
- **Historical patterns**: `data/historical_weather.json`

## Satellite Types

TermiCast supports various weather satellites:

| Satellite | Type | Purpose |
|-----------|------|---------|
| NOAA-18/19/20 | Polar Orbiting | Infrared imaging, cloud detection |
| METOP-A/B/C | Meteorological | Microwave sensing, precipitation |
| GOES satellites | Geostationary | Continuous regional coverage |

## Weather Prediction Models

### Cloud Coverage Analysis
- **Infrared data**: NOAA satellites provide cloud type and coverage
- **Confidence levels**: Based on satellite pass frequency
- **Types**: High altitude, storm clouds, mixed coverage

### Precipitation Prediction
- **Microwave data**: METOP satellites detect moisture content
- **Pressure correlation**: Sensor data enhances accuracy
- **Intensity levels**: Light, moderate, heavy

### Temperature Forecasting
- **Location-based**: Geographic climate patterns
- **Cloud moderation**: Coverage affects temperature extremes
- **Sensor integration**: Real-time calibration

## Best Practices

### For Accurate Predictions:
1. **Update TLE data** regularly (weekly)
2. **Use physical sensors** when possible
3. **Consider elevation** - passes >30° are most reliable
4. **Multiple satellites** provide better coverage

### Location Specification:
```bash
# Preferred formats
termicast forecast --location "City, Country"
termicast forecast --location "Latitude, Longitude"

# Examples
termicast forecast --location "Alexandria, Egypt"
termicast forecast --location "31.2001, 29.9187"
```

### Sensor Setup:
```bash
# Check available ports
ls /dev/tty*

# Configure sensor
termicast sensor --port /dev/ttyUSB0 --enable

# Generate test data if no sensor
termicast sensor  # Follow prompts
```

## Troubleshooting

### Common Issues:

1. **No satellite data**: Check TLE files in `tle/` directory
2. **Geocoding failures**: Verify internet connection or use coordinates
3. **Sensor connection**: Check port permissions and device connection
4. **Low satellite coverage**: Location may have poor satellite visibility

### Debug Information:

```bash
# Check system status
termicast status

# Verify configuration
termicast config-cmd

# Test with known good location
termicast forecast --location "New York, NY"
```

## Advanced Usage

### Automation:
```bash
# Cron job for daily forecasts
0 6 * * * /usr/local/bin/termicast forecast --location "Your City" > daily_forecast.txt
```

### Integration:
- Export data in JSON format for external processing
- Use with home automation systems
- Integrate with alert systems for severe weather

## Example Workflow

```bash
# 1. Initial setup
termicast config-cmd --location "Your City"

# 2. Generate sensor data for testing
termicast sensor
# Select "y" and duration (e.g., 60 minutes)

# 3. Get comprehensive weather analysis
termicast forecast
termicast satellites --today
termicast map
termicast pressure-trend

# 4. Check system health
termicast status
```

## Output Features

### Rich Terminal Display:
- **Colors**: Weather condition coding
- **Unicode**: Weather symbols and indicators
- **Tables**: Formatted data presentation
- **Progress**: Real-time calculation indicators

### Weather Symbols:
- ☀️ Clear skies
- 🌤️ Partly cloudy
- ⛅ Cloudy
- 🌧️ Rain
- ⛈️ Storms
- 🛰️ Satellite indicators

This comprehensive guide covers all major TermiCast functionality. For additional help, use `termicast <command> --help` for command-specific options. 