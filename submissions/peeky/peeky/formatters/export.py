"""
Export functions for Peeky.

This module provides functions to export data in various formats.
"""

import json
import socket
import sys
from typing import Dict, List, Any, Optional

def clean_for_serialization(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Clean connection data for serialization (convert non-serializable types).
    
    Args:
        data: List of connection dictionaries
        
    Returns:
        Cleaned list of dictionaries
    """
    cleaned_data = []
    
    protocol_map = {
        socket.SOCK_STREAM: "TCP",
        socket.SOCK_DGRAM: "UDP"
    }
    
    for item in data:
        cleaned_item = {}
        
        for key, value in item.items():
            if key == "protocol":
                cleaned_item[key] = protocol_map.get(value, str(value))
            elif isinstance(value, (list, dict, set)):
                cleaned_item[key] = value
            else:
                cleaned_item[key] = str(value) if value is not None else None
        
        cleaned_data.append(cleaned_item)
    
    return cleaned_data


def format_as_text(data: List[Dict[str, Any]]) -> str:
    """
    Format connection data as plain text.
    
    Args:
        data: List of connection dictionaries
        
    Returns:
        Formatted text string
    """
    cleaned_data = clean_for_serialization(data)
    
    text = "PEEKY CONNECTION EXPORT\n"
    text += "======================\n\n"
    
    for i, conn in enumerate(cleaned_data, 1):
        text += f"Connection {i}\n"
        text += "-" * (12 + len(str(i))) + "\n"
        
        for key, value in conn.items():
            if isinstance(value, list):
                text += f"{key}: {', '.join(str(v) for v in value)}\n"
            elif isinstance(value, dict):
                text += f"{key}:\n"
                for subkey, subvalue in value.items():
                    text += f"  {subkey}: {subvalue}\n"
            else:
                text += f"{key}: {value}\n"
        
        text += "\n"
    
    return text


def write_export(data: List[Dict[str, Any]], output_file: Optional[str], format_type: str = "text") -> None:
    """
    Export connection data to the specified format.
    
    Args:
        data: List of connection dictionaries
        output_file: Output file path or None for stdout
        format_type: Export format ("json" or "text")
    """
    cleaned_data = clean_for_serialization(data)
    
    if format_type == "json":
        output = json.dumps(cleaned_data, indent=2)
    else:
        output = format_as_text(data)
    
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Data exported to {output_file}")
    else:
        sys.stdout.write(output) 