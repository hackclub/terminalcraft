"""
WHOIS formatting for Peeky.

This module provides functions for formatting WHOIS lookup results.
"""

from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout

from peeky.formatters.tables import COLORS

console = Console()


def format_whois_table(data: Dict[str, Any], lookup_type: str) -> Table:
    """
    Format WHOIS data into a table.
    
    Args:
        data: WHOIS data dictionary
        lookup_type: Type of lookup ("ip" or "domain")
        
    Returns:
        Rich Table object
    """
    title = f"WHOIS Information: {data['target']}"
    table = Table(title=title, show_header=True, header_style=COLORS["header"])
    
    table.add_column("Property", style=COLORS["info"])
    table.add_column("Value", style=COLORS["process"])
    
    table.add_row("Target", data["target"])
    table.add_row("Type", lookup_type.upper())
    
    if lookup_type == "ip":
        table.add_row("Hostname", data.get("hostname", "N/A"))
        table.add_row("Organization", data.get("organization", "N/A"))
        
        location = data.get("location", {})
        location_str = ", ".join(f"{location.get(k, 'Unknown')}" for k in ["city", "region", "country"])
        table.add_row("Location", location_str)
        
        table.add_row("ASN", data.get("asn", "N/A"))
        
        if "netname" in data:
            table.add_row("Network Name", data["netname"])
        
        if "abuse_email" in data:
            table.add_row("Abuse Email", data["abuse_email"])
        if "abuse_phone" in data:
            table.add_row("Abuse Phone", data["abuse_phone"])
    else:
        ip_addresses = ", ".join(data.get("ip_addresses", ["N/A"]))
        table.add_row("IP Addresses", ip_addresses)
        table.add_row("Registrar", data.get("registrar", "N/A"))
        table.add_row("Creation Date", data.get("creation_date", "N/A"))
        table.add_row("Expiration Date", data.get("expiration_date", "N/A"))
        
        name_servers = ", ".join(data.get("name_servers", ["N/A"]))
        table.add_row("Name Servers", name_servers)
        
        if "registrant" in data and isinstance(data["registrant"], dict):
            registrant = data["registrant"]
            table.add_row("Registrant Name", registrant.get("name", "N/A"))
            table.add_row("Registrant Organization", registrant.get("organization", "N/A"))
            if "email" in registrant and registrant["email"] != "Unknown":
                table.add_row("Registrant Email", registrant["email"])
            if "country" in registrant and registrant["country"] != "Unknown":
                table.add_row("Registrant Country", registrant["country"])
    
    if "demo_mode" in data:
        table.add_row("Data Source", "[yellow]Local data (Demo Mode)[/yellow]")
        if "api_message" in data:
            table.add_row("Note", f"[yellow]{data['api_message']}[/yellow]")
        if "get_api_key" in data:
            table.add_row("Get Full Access", f"[cyan]{data['get_api_key']}[/cyan]")
    elif "api_error" in data:
        table.add_row("API Note", f"[yellow]{data['api_error']}[/yellow]")
    
    return table


def format_whois_panel(data: Dict[str, Any], lookup_type: str) -> Panel:
    """
    Format WHOIS data into a rich panel.
    
    Args:
        data: WHOIS data dictionary
        lookup_type: Type of lookup ("ip" or "domain")
        
    Returns:
        Rich Panel object
    """
    content = Text()
    
    content.append("Target: ", style=f"bold {COLORS['info']}")
    content.append(f"{data['target']}\n", style=COLORS["process"])
    
    content.append("Type: ", style=f"bold {COLORS['info']}")
    content.append(f"{lookup_type.upper()}\n\n", style=COLORS["process"])
    
    if lookup_type == "ip":
        content.append("Hostname: ", style=f"bold {COLORS['info']}")
        content.append(f"{data.get('hostname', 'N/A')}\n", style=COLORS["process"])
        
        content.append("Organization: ", style=f"bold {COLORS['info']}")
        content.append(f"{data.get('organization', 'N/A')}\n", style=COLORS["process"])
        
        location = data.get("location", {})
        location_str = ", ".join(f"{location.get(k, 'Unknown')}" for k in ["city", "region", "country"])
        content.append("Location: ", style=f"bold {COLORS['info']}")
        content.append(f"{location_str}\n", style=COLORS["process"])
        
        content.append("ASN: ", style=f"bold {COLORS['info']}")
        content.append(f"{data.get('asn', 'N/A')}\n", style=COLORS["process"])
        
        if "netname" in data:
            content.append("Network Name: ", style=f"bold {COLORS['info']}")
            content.append(f"{data['netname']}\n", style=COLORS["process"])
        
        if "abuse_email" in data:
            content.append("Abuse Email: ", style=f"bold {COLORS['info']}")
            content.append(f"{data['abuse_email']}\n", style=COLORS["process"])
        if "abuse_phone" in data:
            content.append("Abuse Phone: ", style=f"bold {COLORS['info']}")
            content.append(f"{data['abuse_phone']}\n", style=COLORS["process"])
    else:
        content.append("IP Addresses: ", style=f"bold {COLORS['info']}")
        ip_addresses = ", ".join(data.get("ip_addresses", ["N/A"]))
        content.append(f"{ip_addresses}\n", style=COLORS["process"])
        
        content.append("Registrar: ", style=f"bold {COLORS['info']}")
        content.append(f"{data.get('registrar', 'N/A')}\n", style=COLORS["process"])
        
        content.append("Creation Date: ", style=f"bold {COLORS['info']}")
        content.append(f"{data.get('creation_date', 'N/A')}\n", style=COLORS["process"])
        
        content.append("Expiration Date: ", style=f"bold {COLORS['info']}")
        content.append(f"{data.get('expiration_date', 'N/A')}\n", style=COLORS["process"])
        
        content.append("Name Servers: ", style=f"bold {COLORS['info']}")
        name_servers = ", ".join(data.get("name_servers", ["N/A"]))
        content.append(f"{name_servers}\n", style=COLORS["process"])
        
        if "registrant" in data and isinstance(data["registrant"], dict):
            registrant = data["registrant"]
            content.append("\nRegistrant Information:\n", style=f"bold {COLORS['section_title']}")
            
            content.append("Name: ", style=f"bold {COLORS['info']}")
            content.append(f"{registrant.get('name', 'N/A')}\n", style=COLORS["process"])
            
            content.append("Organization: ", style=f"bold {COLORS['info']}")
            content.append(f"{registrant.get('organization', 'N/A')}\n", style=COLORS["process"])
            
            if "email" in registrant and registrant["email"] != "Unknown":
                content.append("Email: ", style=f"bold {COLORS['info']}")
                content.append(f"{registrant['email']}\n", style=COLORS["process"])
            
            if "country" in registrant and registrant["country"] != "Unknown":
                content.append("Country: ", style=f"bold {COLORS['info']}")
                content.append(f"{registrant['country']}\n", style=COLORS["process"])
    
    if "demo_mode" in data:
        content.append("\n[yellow]Demo Mode:[/yellow] ", style="yellow bold")
        if "api_message" in data:
            content.append(f"{data['api_message']}\n", style="yellow")
        else:
            content.append("Running with limited data available\n", style="yellow")
            
        if "get_api_key" in data:
            content.append("[cyan]Get Full Access:[/cyan] ", style="cyan bold")
            content.append(f"{data['get_api_key']}", style="cyan")
    elif "api_error" in data:
        content.append("\n[yellow]API Note: ", style="yellow bold")
        content.append(f"{data['api_error']}[/yellow]", style="yellow")
    
    panel = Panel(
        content,
        title=f"WHOIS Information: {data['target']}",
        border_style=COLORS["info"],
        padding=(1, 2)
    )
    
    return panel


def print_whois_result(data: Dict[str, Any], error: Optional[str], lookup_type: str) -> None:
    """
    Print WHOIS lookup results to the console.
    
    Args:
        data: WHOIS data dictionary
        error: Error message, if any
        lookup_type: Type of lookup ("ip" or "domain")
    """
    console.print("\n[bold]PEEKY WHOIS LOOKUP[/bold]\n", style=COLORS["section_title"])
    
    if error:
        console.print(
            Panel(
                f"Error: {error}",
                title="Lookup Failed",
                border_style=COLORS["error"]
            )
        )
        if "API" in error:
            console.print(
                "[yellow]Hint:[/yellow] Use [bold]--local[/bold] flag to use only local resolution.",
                style=COLORS["info"]
            )
    elif not data:
        console.print(
            Panel(
                "No information found for the provided target.",
                title="No Results",
                border_style=COLORS["warning"]
            )
        )
    else:
        panel = format_whois_panel(data, lookup_type)
        console.print(panel)
    
    console.print() 