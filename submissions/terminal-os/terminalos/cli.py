"""Command-line interface for TerminalOS."""

import click
import sys
import os
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any

from .core.app import TerminalOSApp
from .config.settings import Settings
# from .utils.logger import setup_logger
from .utils.helpers import get_terminal_size, check_dependencies
from . import __version__


def validate_theme(ctx, param, value):
    """Validate theme parameter."""
    valid_themes = ['dark', 'light', 'matrix', 'cyberpunk', 'classic']
    if value not in valid_themes:
        raise click.BadParameter(f'Theme must be one of: {", ".join(valid_themes)}')
    return value


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version and exit')
@click.option('--theme', default='dark', callback=validate_theme,
              help='Theme to use (dark, light, matrix, cyberpunk, classic)')
@click.option('--config', type=click.Path(exists=True), 
              help='Path to custom config file')
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--fullscreen', is_flag=True, help='Start in fullscreen mode')
@click.option('--no-boot', is_flag=True, help='Skip boot animation')
@click.option('--safe-mode', is_flag=True, help='Start in safe mode')
@click.option('--width', type=int, help='Terminal width override')
@click.option('--height', type=int, help='Terminal height override')
@click.pass_context
def cli(ctx, version, theme, config, debug, fullscreen, no_boot, safe_mode, width, height):
    """TerminalOS - A complete operating system experience in your terminal.
    
    🖥️  Features:
    • Desktop Environment with window management
    • File Manager with advanced operations  
    • Text Editor with syntax highlighting
    • Terminal Emulator with command history
    • System Monitor with real-time stats
    • Calculator with scientific functions
    • Music Player with playlist support
    • Package Manager for extensions
    
    Examples:
        terminalos                    # Start TerminalOS
        terminalos --theme matrix     # Start with Matrix theme
        terminalos --debug           # Start with debug logging
        terminalos install cowsay    # Install a package
        terminalos config --editor   # Configure settings
    """
    
    if version:
        click.echo(f"🖥️  TerminalOS v{__version__}")
        click.echo(f"📍 Python {sys.version.split()[0]}")
        click.echo(f"🏠 Config: {Settings.get_config_dir()}")
        sys.exit(0)
    
    # Setup context
    ctx.ensure_object(dict)
    ctx.obj.update({
        'theme': theme,
        'config': config,
        'debug': debug,
        'fullscreen': fullscreen,
        'no_boot': no_boot,
        'safe_mode': safe_mode,
        'width': width,
        'height': height
    })
    
    # Check system requirements
    if not check_dependencies():
        click.echo("❌ System requirements not met. Run 'terminalos doctor' for details.")
        sys.exit(1)
    
    # If no subcommand, run main app
    if ctx.invoked_subcommand is None:
        run_app(ctx.obj)


@cli.command()
@click.option('--app', help='Launch specific app directly')
@click.option('--workspace', help='Load specific workspace')
@click.pass_context
def run(ctx, app, workspace):
    """Start TerminalOS with optional parameters."""
    options = ctx.obj.copy()
    options.update({'direct_app': app, 'workspace': workspace})
    run_app(options)


@cli.command()
@click.argument('package_name', required=False)
@click.option('--upgrade', is_flag=True, help='Upgrade existing package')
@click.option('--force', is_flag=True, help='Force reinstall')
def install(package_name, upgrade, force):
    """Install TerminalOS packages and extensions."""
    from .apps.package_manager import PackageManager
    
    if not package_name:
        # Show available packages
        manager = PackageManager()
        packages = manager.list_available()
        
        click.echo("📦 Available Packages:")
        for pkg in packages:
            status = "✅ Installed" if manager.is_installed(pkg['name']) else "⬜ Available"
            click.echo(f"  {pkg['name']}: {pkg['description']} [{status}]")
        return
    
    manager = PackageManager()
    
    with click.progressbar(length=100, label=f'Installing {package_name}') as bar:
        try:
            success = manager.install(package_name, upgrade=upgrade, force=force, 
                                    progress_callback=lambda p: bar.update(p))
            if success:
                click.echo(f"✅ Successfully installed {package_name}")
            else:
                click.echo(f"❌ Failed to install {package_name}")
        except Exception as e:
            click.echo(f"❌ Error installing {package_name}: {e}")


@cli.command()
@click.argument('package_name')
@click.option('--purge', is_flag=True, help='Remove all data')
def uninstall(package_name, purge):
    """Uninstall TerminalOS packages."""
    from .apps.package_manager import PackageManager
    
    if click.confirm(f'Remove {package_name}?'):
        manager = PackageManager()
        if manager.uninstall(package_name, purge=purge):
            click.echo(f"✅ Successfully removed {package_name}")
        else:
            click.echo(f"❌ Failed to remove {package_name}")


@cli.command()
@click.option('--editor', is_flag=True, help='Open settings editor')
@click.option('--reset', is_flag=True, help='Reset to defaults')
@click.option('--export', type=click.Path(), help='Export settings to file')
@click.option('--import', 'import_file', type=click.Path(exists=True), 
              help='Import settings from file')
def config(editor, reset, export, import_file):
    """Manage TerminalOS configuration."""
    settings = Settings()
    
    if reset:
        if click.confirm('Reset all settings to defaults?'):
            settings.reset_to_defaults()
            click.echo("✅ Settings reset to defaults")
        return
    
    if export:
        settings.export_config(export)
        click.echo(f"✅ Settings exported to {export}")
        return
    
    if import_file:
        settings.import_config(import_file)
        click.echo(f"✅ Settings imported from {import_file}")
        return
    
    if editor:
        # Launch settings app directly
        run_app({'direct_app': 'settings'})
    else:
        # Show current settings
        config_data = settings.get_all()
        click.echo("⚙️  Current TerminalOS Configuration:")
        for section, values in config_data.items():
            click.echo(f"\n[{section}]")
            for key, value in values.items():
                click.echo(f"  {key} = {value}")


@cli.command()
def doctor():
    """Check system requirements and health."""
    click.echo("🔍 TerminalOS System Check\n")
    
    checks = [
        ("Python Version", sys.version_info >= (3, 8)),
        ("Terminal Size", get_terminal_size()[0] >= 80 and get_terminal_size()[1] >= 24),
        ("Config Directory", Settings.get_config_dir().exists()),
        ("Dependencies", check_dependencies()),
    ]
    
    all_good = True
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        click.echo(f"{check_name}: {status}")
        if not result:
            all_good = False
    
    if all_good:
        click.echo("\n🎉 All checks passed! TerminalOS is ready to run.")
    else:
        click.echo("\n⚠️  Some checks failed. Please fix the issues above.")
        sys.exit(1)


@cli.command()
@click.option('--workspace', help='Create new workspace')
@click.option('--theme', help='Create new theme')
@click.option('--app', help='Create new app template')
def create(workspace, theme, app):
    """Create new workspaces, themes, or apps."""
    if workspace:
        create_workspace(workspace)
    elif theme:
        create_theme(theme)  
    elif app:
        create_app_template(app)
    else:
        click.echo("Specify what to create: --workspace, --theme, or --app")


@cli.command()
@click.option('--logs', is_flag=True, help='Show recent logs')
@click.option('--stats', is_flag=True, help='Show usage statistics')
@click.option('--processes', is_flag=True, help='Show TerminalOS processes')
def status(logs, stats, processes):
    """Show TerminalOS status and information."""
    if logs:
        show_recent_logs()
    elif stats:
        show_usage_stats()
    elif processes:
        show_processes()
    else:
        show_general_status()


def run_app(options: Dict[str, Any]):
    """Run the main TerminalOS application."""
    # Setup logging
    log_level = 'DEBUG' if options.get('debug') else 'INFO'
    # setup_logger(level=log_level)
    
    # Create and configure app
    app = TerminalOSApp()
    app.configure(options)
    
    try:
        app.run()
    except KeyboardInterrupt:
        click.echo("\n👋 TerminalOS shutdown")
    except Exception as e:
        if options.get('debug'):
            raise
        click.echo(f"❌ Error: {e}")
        sys.exit(1)


def create_workspace(name: str):
    """Create a new workspace configuration."""
    workspace_dir = Settings.get_config_dir() / "workspaces"
    workspace_dir.mkdir(exist_ok=True)
    
    workspace_file = workspace_dir / f"{name}.json"
    if workspace_file.exists():
        click.echo(f"❌ Workspace '{name}' already exists")
        return
    
    workspace_config = {
        "name": name,
        "apps": [],
        "layout": "default",
        "theme": "dark",
        "created": str(Path.ctime(Path.now()))
    }
    
    workspace_file.write_text(json.dumps(workspace_config, indent=2))
    click.echo(f"✅ Created workspace '{name}'")


def create_theme(name: str):
    """Create a new theme template."""
    theme_dir = Settings.get_config_dir() / "themes"
    theme_dir.mkdir(exist_ok=True)
    
    theme_file = theme_dir / f"{name}.json"
    if theme_file.exists():
        click.echo(f"❌ Theme '{name}' already exists")
        return
    
    # Create basic theme template
    theme_config = {
        "name": name,
        "colors": {
            "primary": "#0066cc",
            "secondary": "#4d94ff",
            "background": "#000000",
            "surface": "#1a1a1a",
            "text": "#ffffff",
            "accent": "#00ff00"
        },
        "styles": {
            "border": "solid",
            "header_style": "bold",
            "button_style": "dim"
        }
    }
    
    theme_file.write_text(json.dumps(theme_config, indent=2))
    click.echo(f"✅ Created theme '{name}' template")


def create_app_template(name: str):
    """Create a new app template."""
    app_dir = Settings.get_config_dir() / "custom_apps"
    app_dir.mkdir(exist_ok=True)
    
    app_file = app_dir / f"{name}.py"
    if app_file.exists():
        click.echo(f"❌ App '{name}' already exists")
        return
    
    template = f'''"""Custom {name} app for TerminalOS."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static
from textual.binding import Binding

from terminalos.apps.base import BaseApp


class {name.title()}App(BaseApp):
    """Custom {name} application."""
    
    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("ctrl+r", "refresh", "Refresh"),
    ]
    
    def __init__(self):
        super().__init__()
        self.title = "{name.title()}"
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"Welcome to {{self.title}}!", classes="welcome")
        yield Footer()
    
    def action_close(self) -> None:
        """Close the application."""
        self.dismiss()
    
    def action_refresh(self) -> None:
        """Refresh the application."""
        # Add refresh logic here
        pass
'''
    
    app_file.write_text(template)
    click.echo(f"✅ Created app template '{name}.py'")


def show_recent_logs():
    """Show recent TerminalOS logs."""
    log_file = Settings.get_config_dir() / "logs" / "terminalos.log"
    if not log_file.exists():
        click.echo("📝 No logs found")
        return
    
    with open(log_file) as f:
        lines = f.readlines()
        for line in lines[-20:]:  # Show last 20 lines
            click.echo(line.rstrip())


def show_usage_stats():
    """Show usage statistics."""
    stats_file = Settings.get_config_dir() / "stats.json"
    if not stats_file.exists():
        click.echo("📊 No usage statistics available")
        return
    
    import json
    with open(stats_file) as f:
        stats = json.load(f)
    
    click.echo("📊 TerminalOS Usage Statistics:")
    click.echo(f"  Total launches: {stats.get('launches', 0)}")
    click.echo(f"  Total runtime: {stats.get('runtime', 0)} minutes")
    click.echo(f"  Most used app: {stats.get('most_used_app', 'N/A')}")


def show_processes():
    """Show TerminalOS related processes."""
    import psutil
    
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'terminalos' in ' '.join(proc.info['cmdline'] or []).lower():
                processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if not processes:
        click.echo("🔍 No TerminalOS processes found")
        return
    
    click.echo("🔄 TerminalOS Processes:")
    for proc in processes:
        click.echo(f"  PID {proc.pid}: {proc.name()}")


def show_general_status():
    """Show general TerminalOS status."""
    settings = Settings()
    
    click.echo("🖥️  TerminalOS Status:")
    click.echo(f"  Version: {__version__}")
    click.echo(f"  Config Dir: {settings.get_config_dir()}")
    click.echo(f"  Current Theme: {settings.get('appearance.theme', 'dark')}")
    click.echo(f"  Debug Mode: {settings.get('system.debug', False)}")
    
    # Check if running
    import psutil
    running = any('terminalos' in p.name().lower() for p in psutil.process_iter())
    status = "🟢 Running" if running else "🔴 Not Running"
    click.echo(f"  Status: {status}")


def main():
    """Main CLI entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()