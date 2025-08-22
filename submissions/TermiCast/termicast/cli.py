import argparse
import sys
import os
from typing import List, Optional
from datetime import datetime
import logging
import time

from rich.console import Console
from rich.panel import Panel
from rich.live import Live

from .config import config, save_config
from .weather import WeatherPredictor
from .satellite import SatelliteTracker
from .visualization import TerminalVisualizer
from .sensors import SensorManager

console = Console()

APP_NAME = "TermiCast"
VERSION = "1.0.0-beta.3"

def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)]
    )
    if verbose:
        console.print("[dim]💡 Verbose logging enabled[/dim]")

def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} - Offline Weather Forecasting with Satellite Data",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    forecast_parser = subparsers.add_parser(
        'forecast',
        help='Get weather forecast for your location',
        description="Get a detailed weather forecast using satellite data and local computations."
    )
    forecast_parser.add_argument(
        '--location', '-l',
        type=str,
        help='Your location (city name or lat,lon)',
        default=config.get('user_preferences.default_location', '')
    )
    forecast_parser.add_argument(
        '--days', '-d',
        type=int,
        default=config.get('forecast.days', 5),
        help='Number of forecast days'
    )
    forecast_parser.add_argument(
        '--compact', '-c',
        action='store_true',
        help='Compact output mode'
    )
    
    sat_parser = subparsers.add_parser(
        'satellite',
        help='Check upcoming satellite passes',
        description='Find upcoming satellite passes for weather data.'
    )
    sat_parser.add_argument(
        '--location', '-l',
        type=str,
        help='Observer location (city or lat,lon)',
        default=config.get('user_preferences.default_location', '')
    )
    sat_parser.add_argument(
        '--hours', '-hr',
        type=int,
        default=config.get('satellite.hours', 24),
        help='Hours to look ahead for passes'
    )
    sat_parser.add_argument(
        '--min-elevation', '-e',
        type=int,
        default=config.get('satellite.min_elevation', 10),
        help='Minimum elevation angle in degrees'
    )
    sat_parser.add_argument(
        '--sat-type', '-t',
        type=str,
        choices=['weather', 'noaa', 'all'],
        default=config.get('satellite.type', 'weather'),
        help='Satellite type to track'
    )
    
    pressure_parser = subparsers.add_parser(
        'pressure',
        help='Check atmospheric pressure trend',
        description='Analyze pressure trend for weather prediction.'
    )
    pressure_parser.add_argument(
        '--hours', '-hr',
        type=int,
        default=12,
        help='Hours of historical data'
    )
    
    map_parser = subparsers.add_parser(
        'map',
        help='Display ASCII weather map',
        description='Show a visual ASCII weather map for your location.'
    )
    map_parser.add_argument(
        '--location', '-l',
        type=str,
        help='Location for weather map (city name or lat,lon)',
        default=config.get('user_preferences.default_location', '')
    )
    
    config_parser = subparsers.add_parser(
        'config',
        help='Manage configuration settings',
        description='View or update configuration settings.'
    )
    config_parser.add_argument(
        '--view', '-v',
        action='store_true',
        help='View current configuration'
    )
    config_parser.add_argument(
        '--set', '-s',
        nargs=2,
        metavar=('KEY', 'VALUE'),
        help='Set a config value'
    )
    config_parser.add_argument(
        '--reset', '-r',
        action='store_true',
        help='Reset to default config'
    )
    
    sensor_parser = subparsers.add_parser(
        'sensor',
        help='Manage environmental sensors',
        description='Interact with local sensors for pressure, temperature, etc.'
    )
    sensor_parser.add_argument(
        '--status', '-st',
        action='store_true',
        help='Check sensor status'
    )
    sensor_parser.add_argument(
        '--enable', '-en',
        action='store_true',
        help='Enable sensor in config'
    )
    sensor_parser.add_argument(
        '--disable', '-dis',
        action='store_true',
        help='Disable sensor in config'
    )
    sensor_parser.add_argument(
        '--port', '-p',
        type=str,
        help='Set sensor port'
    )
    sensor_parser.add_argument(
        '--baudrate', '-b',
        type=int,
        help='Set baudrate'
    )
    sensor_parser.add_argument(
        '--simulate', '-sim',
        type=int,
        metavar='MINUTES',
        help='Simulate sensor data for testing'
    )
    sensor_parser.add_argument(
        '--calibrate', '-cal',
        type=float,
        metavar='REFERENCE_PRESSURE',
        help='Calibrate pressure sensor with reference value'
    )
    sensor_parser.add_argument(
        '--monitor', '-m',
        action='store_true',
        help='Continuously monitor sensor readings'
    )
    
    parser.add_argument(
        '--verbose', '-vb',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--version', '-V',
        action='version',
        version=f"{APP_NAME} v{VERSION}",
        help='Show version info'
    )
    
    return parser.parse_args(args if args is not None else sys.argv[1:])

def display_welcome():
    welcome_text = f"""
[bold cyan]{APP_NAME} v{VERSION}[/bold cyan]
Offline Weather Forecasting with Satellite Data

Use [bold]--help[/bold] for usage or try `{APP_NAME.lower()} forecast` to get started!
💡 [dim]Set a default location with `config --set user_preferences.default_location "Your City"`[/dim]
"""
    console.print(Panel(welcome_text, title="Welcome", style="green", expand=False))

def run_forecast(args: argparse.Namespace, visualizer: TerminalVisualizer, predictor: WeatherPredictor):
    if not args.location:
        console.print("[red]❌ Error: Location is required.[/red]")
        console.print("[dim]💡 Use --location or set a default in config.[/dim]")
        sys.exit(1)
    console.print(f"🌍 Generating forecast for [bold]{args.location}[/bold]...")
    try:
        forecast_data = predictor.generate_forecast(args.location, days=args.days)
        visualizer.display_forecast(forecast_data)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        logging.error(f"Forecast error: {e}", exc_info=True)
        sys.exit(1)

def run_satellite(args: argparse.Namespace, visualizer: TerminalVisualizer, tracker: SatelliteTracker):
    if not args.location:
        console.print("[red]❌ Error: Location is required for satellite tracking.[/red]")
        sys.exit(1)
    console.print(f"🛰️ Checking satellite passes for [bold]{args.location}[/bold] in next {args.hours} hours...")
    try:
        passes = tracker.predict_passes(args.location, duration_hours=args.hours)
        # Filter by minimum elevation if specified
        if args.min_elevation > 10:
            passes = [p for p in passes if p['elevation'] >= args.min_elevation]
        visualizer.display_satellite_passes(passes, title=f"Satellite Passes - Next {args.hours} Hours")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        logging.error(f"Satellite pass error: {e}", exc_info=True)
        sys.exit(1)

def run_pressure(args: argparse.Namespace, visualizer: TerminalVisualizer, sensor_manager: SensorManager):
    console.print(f"📊 Analyzing pressure trend for last {args.hours} hours...")
    try:
        # Get pressure history from sensor manager
        from .weather import weather_predictor
        trend_data = weather_predictor.analyze_pressure_trends(args.hours)
        visualizer.display_pressure_trend(trend_data)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        logging.error(f"Pressure analysis error: {e}", exc_info=True)
        sys.exit(1)

def run_map(args: argparse.Namespace, visualizer: TerminalVisualizer, predictor: WeatherPredictor):
    if not args.location:
        console.print("[red]❌ Error: Location is required for weather map.[/red]")
        console.print("[dim]💡 Use --location or set a default in config.[/dim]")
        sys.exit(1)
    console.print(f"🗺️ Generating ASCII weather map for [bold]{args.location}[/bold]...")
    try:
        # Generate forecast data needed for the map
        forecast_data = predictor.generate_forecast(args.location, days=1)
        visualizer.display_ascii_weather_map(args.location, forecast_data)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        logging.error(f"Weather map error: {e}", exc_info=True)
        sys.exit(1)

def run_config(args: argparse.Namespace):
    if args.view:
        console.print(Panel("Current Configuration", style="bold blue"))
        config_data = config.get_all()
        for section, settings in config_data.items():
            console.print(f"[bold cyan]{section}[/bold cyan]")
            if isinstance(settings, dict):
                for key, value in settings.items():
                    console.print(f"  {key}: [green]{value}[/green]")
            else:
                console.print(f"  [green]{settings}[/green]")
    elif args.reset:
        config.reset_to_defaults()
        console.print("[green]✅ Configuration reset complete.[/green]")
    elif args.set:
        key, value = args.set
        try:
            # Try to convert value to appropriate type
            if value.isdigit():
                value = int(value)
            elif value.replace('.','',1).isdigit():
                value = float(value)
            elif value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            
            config.set(key, value)
            console.print(f"[green]✅ Updated {key} to {value}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            sys.exit(1)
    else:
        console.print("[yellow]⚠️ Use --view, --set, or --reset with config command.[/yellow]")
        sys.exit(1)

def run_sensor(args: argparse.Namespace, sensor_manager: SensorManager, visualizer: TerminalVisualizer):
    if args.status:
        status = sensor_manager.get_sensor_status()
        visualizer.display_sensor_status(status)
    elif args.monitor:
        from rich.panel import Panel
        from rich.console import Group
        try:
            with Live(refresh_per_second=2, console=console) as live:
                while True:
                    status = sensor_manager.get_sensor_status()
                    # Instead of printing, get the Panel from display_sensor_status
                    # We'll need to refactor display_sensor_status to return the Panel
                    panel = visualizer.get_sensor_status_panel(status)
                    live.update(panel)
                    time.sleep(2)
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️ Monitoring stopped by user.[/yellow]")
    elif args.enable:
        config.set('sensor.enabled', True)
        console.print("[green]✅ Sensor enabled.[/green]")
    elif args.disable:
        config.set('sensor.enabled', False)
        console.print("[green]✅ Sensor disabled.[/green]")
    elif args.port:
        config.set('sensor.port', args.port)
        console.print(f"[green]✅ Sensor port set to {args.port}[/green]")
    elif args.baudrate:
        config.set('sensor.baudrate', args.baudrate)
        console.print(f"[green]✅ Baudrate set to {args.baudrate}[/green]")
    elif args.simulate:
        console.print(f"🌀 Simulating sensor data for {args.simulate} minutes...")
        sensor_manager.simulate_sensor_data(args.simulate)
        console.print("[green]✅ Simulation started.[/green]")
    elif args.calibrate:
        console.print(f"⚙️ Calibrating sensor with reference pressure {args.calibrate} mb...")
        success = sensor_manager.calibrate_sensor(args.calibrate)
        if success:
            console.print("[green]✅ Calibration complete.[/green]")
        else:
            console.print("[yellow]⚠️ Calibration failed - sensor not enabled.[/yellow]")
    else:
        console.print("[yellow]⚠️ Use sensor command with an option like --status or --enable.[/yellow]")
        sys.exit(1)

def main(args: Optional[List[str]] = None):
    parsed_args = parse_arguments(args)
    setup_logging(parsed_args.verbose)
    
    if not parsed_args.command:
        display_welcome()
        sys.exit(0)
    
    visualizer = TerminalVisualizer()
    predictor = WeatherPredictor()
    tracker = SatelliteTracker()
    sensor_manager = SensorManager()
    
    if hasattr(parsed_args, 'compact') and parsed_args.compact:
        config.set('user_preferences.compact_mode', True)
    
    command_handlers = {
        'forecast': lambda: run_forecast(parsed_args, visualizer, predictor),
        'satellite': lambda: run_satellite(parsed_args, visualizer, tracker),
        'pressure': lambda: run_pressure(parsed_args, visualizer, sensor_manager),
        'map': lambda: run_map(parsed_args, visualizer, predictor),
        'config': lambda: run_config(parsed_args),
        'sensor': lambda: run_sensor(parsed_args, sensor_manager, visualizer)
    }
    
    if parsed_args.command in command_handlers:
        try:
            command_handlers[parsed_args.command]()
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️ Operation cancelled by user.[/yellow]")
            sys.exit(1)
        except Exception as e:
            console.print(f"\n[red]❌ Unexpected error: {e}[/red]")
            logging.error(f"Unexpected error in {parsed_args.command}: {e}", exc_info=True)
            sys.exit(1)
    else:
        console.print(f"[red]❌ Unknown command: {parsed_args.command}[/red]")
        sys.exit(1)
    
    sensor_manager.close()

if __name__ == "__main__":
    main()
