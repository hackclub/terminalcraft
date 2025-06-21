"""
WHOIS and IP information functions for Peeky.

This module provides functions to lookup information about IP addresses and domains.
"""

import re
import socket
import requests
import json
from typing import Dict, List, Any, Tuple, Optional, Union

from peeky.core.config import get_api_key

def is_valid_ipv4(ip: str) -> bool:
    """
    Check if a string is a valid IPv4 address.
    
    Args:
        ip: String to check
        
    Returns:
        True if valid IPv4 address, False otherwise
    """
    pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
    match = re.match(pattern, ip)
    if not match:
        return False
    
    for i in range(1, 5):
        octet = int(match.group(i))
        if octet < 0 or octet > 255:
            return False
    
    return True


def is_valid_domain(domain: str) -> bool:
    """
    Check if a string is a valid domain name.
    
    Args:
        domain: String to check
        
    Returns:
        True if valid domain, False otherwise
    """
    pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    return bool(re.match(pattern, domain))


def get_whois_from_api(target: str, is_ip: bool = False) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Get WHOIS information from the APILayer API.
    
    Args:
        target: IP address or domain to look up
        is_ip: Whether the target is an IP address
        
    Returns:
        Tuple of (result_data, error_message)
    """
    api_key = get_api_key("whois")
    if not api_key:
        return {
            "demo_mode": True,
            "message": "Running in demo mode with limited data. Get an API key for full features.",
            "get_api_key": "Visit https://apilayer.com/marketplace/whois-api for a free API key"
        }, None
    
    if is_ip:
        return {
            "demo_mode": True,
            "message": "The WHOIS API does not support direct IP address lookups. Using local resolution instead."
        }, None
    
    url = f"https://api.apilayer.com/whois/query?domain={target}"
    
    headers = {"apikey": api_key}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'result' in data:
                return data['result'], None
            else:
                return data, None
        else:
            error_message = f"API request failed with status code {response.status_code}"
            if response.status_code == 401:
                error_message = "Invalid API key. Please update your API key with 'peeky config --set-whois-key'"
            elif response.status_code == 429:
                error_message = "API rate limit exceeded. Please try again later."
            
            return {}, error_message
    except requests.exceptions.RequestException as e:
        return {}, f"Request error: {str(e)}"
    except ValueError as e:
        return {}, f"Failed to parse API response: {str(e)}"


def get_ip_info(ip: str) -> Dict[str, Any]:
    """
    Get information about an IP address using local resolution.
    
    Args:
        ip: IP address to look up
        
    Returns:
        Dictionary with IP information
    """
    result = {
        "target": ip,
        "type": "ip",
    }
    
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        result["hostname"] = hostname
        
        parts = hostname.split('.')
        if len(parts) >= 2:
            org = parts[-2]
            if org not in ('com', 'net', 'org', 'edu', 'gov', 'mil'):
                result["organization"] = org.capitalize()
    except socket.herror:
        result["hostname"] = "No hostname found"
    
    result["location"] = {
        "country": "Unknown",
        "region": "Unknown",
        "city": "Unknown"
    }
    result["asn"] = "Unknown"
    
    if ip == "8.8.8.8" or ip == "8.8.4.4":
        result["organization"] = "Google LLC"
        result["location"]["country"] = "United States"
        result["asn"] = "AS15169"
        result["netname"] = "GOOGLE"
        result["abuse_email"] = "network-abuse@google.com"
    elif ip.startswith("192.168.") or ip.startswith("10.") or ip == "127.0.0.1":
        result["organization"] = "Private Network"
        result["location"]["country"] = "Local"
        result["asn"] = "Private"
        result["netname"] = "PRIVATE-NETWORK"
    
    return result


def perform_lookup(target: str, use_api: bool = True) -> Tuple[Dict[str, Any], Optional[str], str]:
    """
    Perform a lookup for an IP address or domain.
    
    Args:
        target: IP address or domain to look up
        use_api: Whether to use the external API (if available)
        
    Returns:
        Tuple of (result_data, error_message, lookup_type)
    """
    lookup_type = ""
    if is_valid_ipv4(target):
        lookup_type = "ip"
    elif is_valid_domain(target):
        lookup_type = "domain"
    else:
        return {}, f"Invalid input: '{target}' is not a valid IP address or domain name", ""
    
    if lookup_type == "ip":
        result = get_ip_info(target)
        return result, None, lookup_type
    
    result = {
        "target": target,
        "type": lookup_type,
    }
    
    try:
        ip_addresses = socket.gethostbyname_ex(target)[2]
        result["ip_addresses"] = ip_addresses
    except socket.herror:
        return {}, f"Could not resolve domain: {target}", lookup_type
    
    if use_api:
        api_data, error = get_whois_from_api(target, is_ip=False)
        
        if api_data and "demo_mode" in api_data:
            result["demo_mode"] = True
            result["api_message"] = api_data.get("message", "Using local data")
            if "get_api_key" in api_data:
                result["get_api_key"] = api_data["get_api_key"]
            
            result = _add_placeholder_data(result)
        elif error:
            return {}, error, lookup_type
        elif api_data:
            result = _extract_api_data(api_data, result)
    else:
        result = _add_placeholder_data(result)
    
    return result, None, lookup_type


def _extract_api_data(api_data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant information from API response.
    
    Args:
        api_data: API response data
        result: Current result dictionary
        
    Returns:
        Updated result dictionary
    """
    if "registrar" in api_data:
        result["registrar"] = api_data["registrar"]
    if "creation_date" in api_data:
        result["creation_date"] = api_data["creation_date"]
    elif "created_date" in api_data:
        result["creation_date"] = api_data["created_date"]
    
    if "expiration_date" in api_data:
        result["expiration_date"] = api_data["expiration_date"]
    elif "expiry_date" in api_data:
        result["expiration_date"] = api_data["expiry_date"]
    
    if "name_servers" in api_data:
        if isinstance(api_data["name_servers"], list):
            result["name_servers"] = api_data["name_servers"]
        elif isinstance(api_data["name_servers"], str):
            result["name_servers"] = [api_data["name_servers"]]
    
    if "registrant" in api_data and isinstance(api_data["registrant"], dict):
        registrant = api_data["registrant"]
        result["registrant"] = {
            "name": registrant.get("name", "Unknown"),
            "organization": registrant.get("organization", "Unknown"),
            "email": registrant.get("email", "Unknown"),
            "country": registrant.get("country", "Unknown")
        }
    
    if "registrar" not in result:
        result["registrar"] = "Unknown"
    if "creation_date" not in result:
        result["creation_date"] = "Unknown"
    if "expiration_date" not in result:
        result["expiration_date"] = "Unknown"
    if "name_servers" not in result:
        result["name_servers"] = []
    
    return result


def _add_placeholder_data(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add placeholder data for demo mode or local lookups.
    
    Args:
        result: Current result dictionary
        
    Returns:
        Updated result dictionary with placeholder data
    """
    if "registrar" not in result:
        result["registrar"] = "Example Registrar"
    if "creation_date" not in result:
        result["creation_date"] = "Unknown"
    if "expiration_date" not in result:
        result["expiration_date"] = "Unknown"
    if "name_servers" not in result:
        result["name_servers"] = ["ns1.example.com", "ns2.example.com"]
    
    return result