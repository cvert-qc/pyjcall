"""
Utilities for handling date and datetime conversions between Python objects and JustCall API formats.

JustCall API date format: "2020-12-15"
JustCall API datetime format: "2020-12-03 14:46:52"
"""

from datetime import date, datetime
from typing import Optional, Union, Any, Dict


def to_api_date(value: Optional[date]) -> Optional[str]:
    """
    Convert a Python date object to JustCall API date format.
    
    Args:
        value: Python date object or None
        
    Returns:
        String in format "YYYY-MM-DD" or None if input is None
    """
    if value is None:
        return None
    return value.strftime("%Y-%m-%d")


def to_api_datetime(value: Optional[datetime]) -> Optional[str]:
    """
    Convert a Python datetime object to JustCall API datetime format.
    
    Args:
        value: Python datetime object or None
        
    Returns:
        String in format "YYYY-MM-DD HH:MM:SS" or None if input is None
    """
    if value is None:
        return None
    return value.strftime("%Y-%m-%d %H:%M:%S")


def from_api_date(value: Optional[str]) -> Optional[date]:
    """
    Convert a JustCall API date string to Python date object.
    
    Args:
        value: String in format "YYYY-MM-DD" or None
        
    Returns:
        Python date object or None if input is None
    """
    if not value:
        return None
    return date.fromisoformat(value)


def from_api_datetime(value: Optional[str]) -> Optional[datetime]:
    """
    Convert a JustCall API datetime string to Python datetime object.
    
    Args:
        value: String in format "YYYY-MM-DD HH:MM:SS" or None
        
    Returns:
        Python datetime object or None if input is None
    """
    if not value:
        return None
    try:
        # Try the full datetime format first
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        # If that fails, try just the date format
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid datetime format: {value}. Expected 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD'")


def convert_dict_datetimes(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively convert all date/datetime strings in a dictionary to Python objects.
    
    This is useful for processing API responses.
    
    Args:
        data: Dictionary potentially containing date/datetime strings
        
    Returns:
        Dictionary with date/datetime strings converted to Python objects
    """
    if not isinstance(data, dict):
        return data
    
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Try to convert string to datetime or date
            try:
                if " " in value and len(value) >= 16:  # Likely a datetime
                    result[key] = from_api_datetime(value)
                elif "-" in value and len(value) == 10:  # Likely a date
                    result[key] = from_api_date(value)
                else:
                    result[key] = value
            except ValueError:
                result[key] = value
        elif isinstance(value, dict):
            result[key] = convert_dict_datetimes(value)
        elif isinstance(value, list):
            result[key] = [convert_dict_datetimes(item) if isinstance(item, dict) else item for item in value]
        else:
            result[key] = value
    
    return result
