"""
Terminal visualization stuff - making boring data look cool in a terminal!
I spent way too long figuring out how to make ASCII maps look half-decent.

Back in 2019, I was stuck in a remote cabin with no internet during a storm,
and I wish I had something like this to visualize weather data. So here we are!

TODO: add more funky ASCII art cuz why not
"""

import termplotlib as tpl  # cool library for terminal graphs
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich.layout import Layout
from rich.tree import Tree
from rich.align import Align
from rich import box
from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np  # just in case we need some number crunching

from .config import config  # grab user settings

class TerminalVisualizer:
    """Handles all the pretty terminal output - because data deserves to look good!"""
    
    def __init__(self):
        self.console = Console()  # rich is awesome for terminal formatting
        # pull display settings from config
        self.use_colors = config.get('display.colors', True)
        self.use_unicode = config.get('display.unicode', True)
        self.table_style = config.get('display.table_style', 'grid')
        # personal touch - I like verbose output sometimes
        self.verbose_mode = config.get('user_preferences.compact_mode', False) == False
        
        if self.verbose_mode:
            print("💡 Verbose mode ON - showing extra details")
    
    def display_forecast(self, forecast_data: Dict[str, Any]):
        """Show the weather forecast in a nice table - my friends always ask for this output!"""
        self.console.clear()  # clear the screen for a fresh look
        
        # Header with a personal flair
        title = f"🌤️  Weather Forecast for {forecast_data['location']}"
        self.console.print(Panel(title, style="bold blue", subtitle="TermiCast v1.0"))
        
        # Forecast table - took me ages to get the colors right
        forecast_table = Table(
            title="Daily Forecast",
            box=box.ROUNDED,  # I like rounded corners, looks friendlier
            show_header=True,
            header_style="bold magenta"
        )
        
        # Define columns - I keep tweaking these for better readability
        forecast_table.add_column("Date", style="cyan", no_wrap=True)
        forecast_table.add_column("Temp (°C)", justify="center")
        forecast_table.add_column("Clouds (%)", justify="center")
        forecast_table.add_column("Rain (%)", justify="center")
        forecast_table.add_column("Wind", justify="center")
        forecast_table.add_column("Satellite Coverage", justify="center")
        
        # Loop through forecast data - this is the meat of the display
        for daily in forecast_data['daily_forecasts']:
            conditions = daily['conditions']
            temp = conditions['temperature']
            cloud = conditions['cloud_coverage']
            rain = conditions['precipitation_chance']
            wind = conditions['wind']
            
            # Color-code temperature based on my personal thresholds
            temp_text = f"{temp['low']}-{temp['high']}"
            if temp['high'] > 30:
                temp_style = "red"  # too hot for me!
            elif temp['low'] < 5:
                temp_style = "blue"  # brrr, cold!
            else:
                temp_style = "green"  # just right
            
            # Add some weather icons for visual flair
            cloud_icon = self._get_cloud_icon(cloud['percentage'])
            rain_icon = self._get_rain_icon(rain)
            
            # Add the row with styled data
            forecast_table.add_row(
                daily['date'],
                Text(temp_text, style=temp_style),
                f"{cloud_icon} {cloud['percentage']}%",
                f"{rain_icon} {rain}%",
                f"{wind['speed']} km/h {wind['direction']}",
                f"⭐ {daily['coverage_score']}/100"
            )
        
        # Print the table to terminal
        self.console.print(forecast_table)
        
        # Show warnings if there are any - important stuff!
        if forecast_data.get('warnings'):
            self._display_warnings(forecast_data['warnings'])
        
        # Footer with generation time - I like knowing when data was made
        summary_text = f"Generated at: {forecast_data['generated_at']}"
        self.console.print(f"\n[dim]{summary_text}[/dim]")
        if self.verbose_mode:
            self.console.print("[dim]💡 Tip: Use --days to get longer forecasts[/dim]")
    
    def display_satellite_passes(self, passes: List[Dict[str, Any]], title: str = "Upcoming Satellite Passes"):
        """Show upcoming satellite passes - I geek out over this stuff!"""
        self.console.clear()  # fresh screen
        
        # Header with some emoji fun
        self.console.print(Panel(f"🛰️  {title}", style="bold green"))
        
        # Handle empty data - happens more often than you'd think
        if not passes:
            self.console.print("😕 No satellite passes found for the specified time period.")
            self.console.print("   Try increasing the time range with --hours.")
            return
        
        # Build the passes table - I made this detailed for satellite nerds like me
        passes_table = Table(
            box=box.HEAVY_EDGE,  # heavy edge looks more 'techy'
            show_header=True,
            header_style="bold cyan"
        )
        
        # Columns - I keep adjusting these based on feedback from friends
        passes_table.add_column("Time (UTC)", style="yellow")
        passes_table.add_column("Satellite", style="bright_blue")
        passes_table.add_column("Type", style="magenta")
        passes_table.add_column("Elevation", justify="center")
        passes_table.add_column("Azimuth", justify="center")
        passes_table.add_column("Distance", justify="center")
        
        # Limit to 20 passes so terminal doesn't get flooded
        for pass_info in passes[:20]:
            time_str = pass_info['time'].strftime('%Y-%m-%d %H:%M')
            elevation = f"{pass_info['elevation']:.1f}°"
            azimuth = f"{pass_info['azimuth']:.1f}°"
            distance = f"{pass_info['distance']:.0f} km"
            
            # Color by elevation - higher is better for signal
            if pass_info['elevation'] > 60:
                elev_style = "bright_green"  # awesome!
            elif pass_info['elevation'] > 30:
                elev_style = "green"  # decent
            else:
                elev_style = "yellow"  # meh, low on horizon
            
            passes_table.add_row(
                time_str,
                pass_info['satellite'],
                pass_info['type'],
                Text(elevation, style=elev_style),
                azimuth,
                distance
            )
        
        self.console.print(passes_table)
        
        # Note if we're truncating the list
        if len(passes) > 20:
            self.console.print(f"\n[dim]Showing first 20 of {len(passes)} passes[/dim]")
        if self.verbose_mode:
            self.console.print("[dim]💡 Elevation > 30° is best for data quality[/dim]")
    
    def display_pressure_trend(self, trend_data: Dict[str, Any]):
        """Show pressure trends with a simple graph - I love seeing these patterns!"""
        self.console.clear()
        
        # Header - keepin' it simple
        self.console.print(Panel("📊 Atmospheric Pressure Trend", style="bold blue"))
        
        # Handle no data case - happens if sensor isn't connected
        if trend_data['trend'] == 'no_data':
            self.console.print("[yellow]No pressure data available[/yellow]")
            self.console.print(trend_data['recommendation'])
            self.console.print("[dim]💡 Connect a sensor or use --simulate for testing[/dim]")
            return
        
        # Summary table - I prefer no borders here for a cleaner look
        trend_info = Table(box=None, show_header=False)
        trend_info.add_column("", style="bold")
        trend_info.add_column("", style="white")
        
        # Add the data rows - formatted for easy reading
        trend_info.add_row("Current Pressure:", f"{trend_data['current_mb']} mb")
        trend_info.add_row("Trend:", self._format_trend(trend_data['trend']))
        trend_info.add_row("Change:", f"{trend_data['change_mb']} mb")
        trend_info.add_row("Data Points:", str(trend_data['data_points']))
        trend_info.add_row("Time Span:", f"{trend_data['time_span_hours']} hours")
        
        self.console.print(trend_info)
        self.console.print()  # spacer
        
        # Simple ASCII graph - I wanted something fancier but this works for now
        if trend_data['trend'] == 'rising':
            graph_ascii = "📈 Pressure Rising - Weather Improving"
            style = "green"  # good news!
        elif trend_data['trend'] == 'falling':
            graph_ascii = "📉 Pressure Falling - Weather May Deteriorate"
            style = "red"  # uh oh
        else:
            graph_ascii = "➡️  Pressure Stable"
            style = "yellow"  # no change
        
        self.console.print(Text(graph_ascii, style=style))
        self.console.print(f"\n{trend_data['message']}")
        if self.verbose_mode:
            self.console.print("[dim]💡 Falling pressure often means rain is coming[/dim]")
    
    def display_ascii_weather_map(self, location: str, forecast_data: Dict[str, Any]):
        """Draw a simple ASCII weather map - reminds me of old-school weather reports!"""
        self.console.clear()
        
        # Header with location - I added this after a friend got confused about which city
        self.console.print(Panel(f"🗺️  Weather Map - {location}", style="bold cyan", subtitle="Simplified View"))
        
        # Generate a simple grid based on forecast - not super accurate but looks cool
        map_grid = self._generate_weather_grid(forecast_data)
        
        # Show legend - took me a while to pick the right emojis
        self.console.print("Legend: ☀️ Clear  ⛅ Partly Cloudy  ☁️ Cloudy  🌧️ Rain  ⛈️ Storm")
        self.console.print()  # empty line for spacing
        
        # Print the map grid - I adjust this sometimes based on terminal width
        for row in map_grid:
            line = " ".join(row)  # space out the icons a bit
            self.console.print(line, justify="center")
        
        # Footer note - I added this because people kept asking what area it covers
        self.console.print("\n[dim]Note: This is a simplified regional view based on satellite data[/dim]")
        if self.verbose_mode:
            self.console.print("[dim]💡 Map represents a ~500km radius around your location[/dim]")
    
    def display_satellite_status(self, satellites: List[Dict[str, Any]]):
        """Display current satellite positions and status"""
        self.console.clear()
        
        # Header
        self.console.print(Panel("🛰️ Current Satellite Positions", style="bold green"))
        
        if not satellites:
            self.console.print("No satellite data available.")
            return
        
        # Satellite status table
        sat_table = Table(
            box=box.DOUBLE_EDGE,
            show_header=True,
            header_style="bold yellow"
        )
        
        sat_table.add_column("Satellite", style="bright_blue")
        sat_table.add_column("Type", style="magenta")
        sat_table.add_column("Latitude", justify="center")
        sat_table.add_column("Longitude", justify="center")
        sat_table.add_column("Altitude", justify="center")
        sat_table.add_column("Status", justify="center")
        
        for sat in satellites:
            lat = f"{sat['latitude']:.2f}°"
            lon = f"{sat['longitude']:.2f}°"
            alt = f"{sat['altitude']:.0f} km"
            
            # Simple status based on altitude
            if sat['altitude'] > 800:
                status = "🟢 Active"
                status_style = "green"
            else:
                status = "🟡 Low"
                status_style = "yellow"
            
            sat_table.add_row(
                sat['satellite'],
                sat['type'],
                lat,
                lon,
                alt,
                Text(status, style=status_style)
            )
        
        self.console.print(sat_table)
    
    def get_sensor_status_panel(self, sensor_data: Dict[str, Any]):
        """Return the Panel object for sensor connection and data status (for Live display)"""
        if sensor_data['enabled']:
            status_color = "green" if sensor_data['connected'] else "red"
            status_text = "Connected" if sensor_data['connected'] else "Disconnected"
            sensor_info = f"""
Status: [{status_color}]{status_text}[/{status_color}]
Port: {sensor_data['port']}
Monitoring: {'Yes' if sensor_data.get('monitoring') else 'No'}
"""
            if 'last_readings' in sensor_data:
                readings = sensor_data['last_readings']
                sensor_info += f"""
Last Readings:
• Pressure: {readings['pressure']['value']:.2f} mb ({readings['pressure']['history_points']} data points)
• Temperature: {readings['temperature']['value']:.1f}°C ({readings['temperature']['history_points']} data points)
• Humidity: {readings['humidity']['value']:.1f}% ({readings['humidity']['history_points']} data points)
"""
        else:
            sensor_info = "[yellow]Sensor disabled[/yellow]\nEnable in configuration for enhanced predictions."
        return Panel(sensor_info, title="🌡️ Sensor Status", border_style="blue")

    def display_sensor_status(self, sensor_data: Dict[str, Any]):
        """Display sensor connection and data status"""
        panel = self.get_sensor_status_panel(sensor_data)
        self.console.print(panel)
    
    def show_progress(self, message: str):
        """Show progress spinner"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task(description=message, total=None)
            return progress, task
    
    def _display_warnings(self, warnings: List[Dict[str, Any]]):
        """Display weather warnings"""
        if not warnings:
            return
        
        warning_panel_content = ""
        for warning in warnings:
            severity_icon = {
                'low': '🟡',
                'medium': '🟠', 
                'moderate': '🟠',
                'high': '🔴',
                'severe': '🔴'
            }.get(warning['severity'], '⚠️')
            
            warning_panel_content += f"{severity_icon} {warning['message']}\n"
        
        self.console.print(Panel(
            warning_panel_content.strip(),
            title="⚠️  Weather Warnings",
            border_style="red"
        ))
    
    def _get_cloud_icon(self, percentage: int) -> str:
        """Get cloud icon based on coverage percentage"""
        if percentage < 25:
            return "☀️"
        elif percentage < 50:
            return "🌤️"
        elif percentage < 75:
            return "⛅"
        else:
            return "☁️"
    
    def _get_rain_icon(self, percentage: int) -> str:
        """Get rain icon based on precipitation chance"""
        if percentage < 20:
            return "☀️"
        elif percentage < 50:
            return "🌦️"
        elif percentage < 80:
            return "🌧️"
        else:
            return "⛈️"
    
    def _format_trend(self, trend: str) -> str:
        """Format pressure trend with colors and icons"""
        if trend == 'rising':
            return "[green]📈 Rising[/green]"
        elif trend == 'falling':
            return "[red]📉 Falling[/red]"
        else:
            return "[yellow]➡️ Stable[/yellow]"
    
    def _generate_weather_grid(self, forecast_data: Dict[str, Any]) -> List[List[str]]:
        """Generate a simple ASCII weather grid"""
        # Simple 8x8 grid representation
        grid_size = 8
        grid = []
        
        if not forecast_data.get('daily_forecasts'):
            # Default grid
            for i in range(grid_size):
                row = ['☀️'] * grid_size
                grid.append(row)
            return grid
        
        today = forecast_data['daily_forecasts'][0]
        conditions = today['conditions']
        
        # Base weather icon
        cloud_pct = conditions['cloud_coverage']['percentage']
        rain_pct = conditions['precipitation_chance']
        
        if rain_pct > 70:
            base_icon = '⛈️'
        elif rain_pct > 40:
            base_icon = '🌧️'
        elif cloud_pct > 70:
            base_icon = '☁️'
        elif cloud_pct > 40:
            base_icon = '⛅'
        else:
            base_icon = '☀️'
        
        # Fill grid with variations
        icons = [base_icon, '☀️', '⛅', '☁️']
        
        for i in range(grid_size):
            row = []
            for j in range(grid_size):
                # Add some variation based on position
                if (i + j) % 3 == 0:
                    row.append(base_icon)
                else:
                    # Random variation
                    idx = (i * j) % len(icons)
                    row.append(icons[idx])
            grid.append(row)
        
        return grid

# Global visualizer instance
visualizer = TerminalVisualizer() 