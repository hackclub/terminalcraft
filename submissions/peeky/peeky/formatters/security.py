"""
Security formatting for Peeky.

This module provides functions for formatting security scan results.
"""

from typing import Dict, List, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from peeky.formatters.tables import COLORS

console = Console()


def format_security_table(exposed_services: List[Dict[str, Any]]) -> Table:
    """
    Format exposed services into a table.
    
    Args:
        exposed_services: List of exposed service dictionaries
        
    Returns:
        Rich Table object
    """
    table = Table(title="Security Scan Results", show_header=True, header_style=COLORS["header"])
    
    table.add_column("Port", style=COLORS["port"])
    table.add_column("Service", style=COLORS["process"])
    table.add_column("Risk", style=COLORS["warning"])
    table.add_column("Address", style=COLORS["address"])
    table.add_column("Process", style=COLORS["process"])
    table.add_column("PID", style=COLORS["pid"])
    
    risk_style = {
        "critical": f"bold {COLORS['error']}",
        "high": COLORS["error"],
        "medium": COLORS["warning"],
        "low": COLORS["success"]
    }
    
    for service in exposed_services:
        port = str(service["port"])
        service_name = service["service"]
        risk = service["risk"]
        address = service["address"]
        process = service["process"]
        pid = str(service["pid"]) if service["pid"] else "-"
        
        style = risk_style.get(risk, COLORS["info"])
        
        table.add_row(
            port,
            service_name,
            f"[{style}]{risk.upper()}[/{style}]",
            address,
            process,
            pid
        )
    
    return table


def format_recommendations(recommendations: List[str]) -> Panel:
    """
    Format security recommendations into a panel.
    
    Args:
        recommendations: List of recommendation strings
        
    Returns:
        Rich Panel object
    """
    content = Text()
    
    for i, rec in enumerate(recommendations, 1):
        if i > 1:
            content.append("\n\n")
        content.append(f"{i}. ", style=f"bold {COLORS['info']}")
        content.append(rec)
    
    panel = Panel(
        content,
        title="Security Recommendations",
        border_style=COLORS["warning"],
        padding=(1, 2)
    )
    
    return panel


def print_security_results(exposed_services: List[Dict[str, Any]], recommendations: List[str]) -> None:
    """
    Print security scan results to the console.
    
    Args:
        exposed_services: List of exposed service dictionaries
        recommendations: List of recommendation strings
    """
    console.print("\n[bold]PEEKY SECURITY SCAN[/bold]\n", style=COLORS["section_title"])
    
    if not exposed_services:
        console.print(
            Panel(
                "No significant security issues detected. Your system appears to be configured securely.",
                title="Security Scan Results",
                border_style=COLORS["success"]
            )
        )
    else:
        table = format_security_table(exposed_services)
        console.print(table)
        
        high_risk = sum(1 for s in exposed_services if s["risk"] in ("high", "critical"))
        medium_risk = sum(1 for s in exposed_services if s["risk"] == "medium")
        low_risk = sum(1 for s in exposed_services if s["risk"] == "low")
        
        console.print()
        console.print("Risk Summary:", style=f"bold {COLORS['section_title']}")
        if high_risk > 0:
            console.print(f"  [bold {COLORS['error']}]High Risk:[/] {high_risk} services")
        if medium_risk > 0:
            console.print(f"  [bold {COLORS['warning']}]Medium Risk:[/] {medium_risk} services")
        if low_risk > 0:
            console.print(f"  [bold {COLORS['success']}]Low Risk:[/] {low_risk} services")
        
    console.print()
    console.print(format_recommendations(recommendations))
    console.print()