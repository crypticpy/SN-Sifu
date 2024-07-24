"""
utils.py

This module contains utility functions that can be used across the KB Article
and Ticket Processing System.

Author: Principal Python Engineer
Date: 2024-07-14
"""

import re
from typing import Any, Dict, List
from datetime import datetime
import hashlib
import json

def sanitize_string(text: str) -> str:
    """
    Sanitize a string by removing special characters and extra whitespace.

    Args:
    text (str): The input string to sanitize.

    Returns:
    str: The sanitized string.
    """
    # Remove special characters
    text = re.sub(r'[^\w\s]', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text.lower()

def validate_date(date_string: str) -> bool:
    """
    Validate if a string is in the correct date format (YYYY-MM-DD).

    Args:
    date_string (str): The date string to validate.

    Returns:
    bool: True if the date is valid, False otherwise.
    """
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def generate_id(data: Dict[str, Any]) -> str:
    """
    Generate a unique ID for an item based on its content.

    Args:
    data (Dict[str, Any]): The data dictionary to generate an ID for.

    Returns:
    str: A unique ID string.
    """
    # Convert the dictionary to a JSON string
    json_string = json.dumps(data, sort_keys=True)
    # Generate a SHA256 hash of the JSON string
    return hashlib.sha256(json_string.encode()).hexdigest()

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """
    Flatten a nested dictionary.

    Args:
    d (Dict[str, Any]): The dictionary to flatten.
    parent_key (str): The parent key for nested dictionaries.
    sep (str): The separator to use between keys.

    Returns:
    Dict[str, Any]: A flattened dictionary.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of a specified size.

    Args:
    lst (List[Any]): The list to split.
    chunk_size (int): The size of each chunk.

    Returns:
    List[List[Any]]: A list of chunks.
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def safe_get(dct: Dict[str, Any], *keys) -> Any:
    """
    Safely get a value from a nested dictionary.

    Args:
    dct (Dict[str, Any]): The dictionary to search.
    *keys: The keys to traverse.

    Returns:
    Any: The value if found, None otherwise.
    """
    for key in keys:
        try:
            dct = dct[key]
        except (KeyError, TypeError):
            return None
    return dct

def truncate_string(s: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate a string to a specified maximum length.

    Args:
    s (str): The string to truncate.
    max_length (int): The maximum length of the string.
    suffix (str): The suffix to add to truncated strings.

    Returns:
    str: The truncated string.
    """
    if len(s) <= max_length:
        return s
    return s[:max_length-len(suffix)] + suffix

def parse_date_range(date_range: str) -> tuple:
    """
    Parse a date range string into start and end dates.

    Args:
    date_range (str): A string representing a date range (e.g., '2024-01-01 to 2024-12-31').

    Returns:
    tuple: A tuple containing start_date and end_date as datetime objects.
    """
    start_str, end_str = date_range.split(' to ')
    start_date = datetime.strptime(start_str.strip(), '%Y-%m-%d')
    end_date = datetime.strptime(end_str.strip(), '%Y-%m-%d')
    return start_date, end_date

# Example usage
if __name__ == "__main__":
    # Test sanitize_string
    print(sanitize_string("Hello, World! 123"))  # Output: hello world 123

    # Test validate_date
    print(validate_date("2024-07-14"))  # Output: True
    print(validate_date("2024/07/14"))  # Output: False

    # Test generate_id
    data = {"name": "John Doe", "age": 30}
    print(generate_id(data))  # Output: a unique hash

    # Test flatten_dict
    nested_dict = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
    print(flatten_dict(nested_dict))  # Output: {'a': 1, 'b_c': 2, 'b_d_e': 3}

    # Test chunk_list
    numbers = list(range(10))
    print(chunk_list(numbers, 3))  # Output: [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]

    # Test safe_get
    data = {"user": {"name": "John", "address": {"city": "New York"}}}
    print(safe_get(data, "user", "address", "city"))  # Output: New York
    print(safe_get(data, "user", "address", "country"))  # Output: None

    # Test truncate_string
    long_string = "This is a very long string that needs to be truncated"
    print(truncate_string(long_string, 20))  # Output: This is a very lon...

    # Test parse_date_range
    date_range = "2024-01-01 to 2024-12-31"
    start, end = parse_date_range(date_range)
    print(f"Start: {start}, End: {end}")  # Output: Start and end datetime objects
