"""
Environment variable utilities for CozyWish.

This module provides utilities for working with environment variables using python-dotenv.
It maintains compatibility with python-decouple for existing code.
"""

import os
import logging
from pathlib import Path
from typing import Any, Optional, Union, List, Dict, Type, cast

# Import dotenv for loading environment variables from .env file
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

# Define the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
def load_env(env_file: Optional[Union[str, Path]] = None) -> None:
    """
    Load environment variables from .env file.
    
    Args:
        env_file: Path to .env file. If None, tries to find .env in the project root.
    """
    if env_file is None:
        env_file = BASE_DIR / '.env'
    
    env_path = Path(env_file)
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        logger.info(f"Loaded environment variables from {env_path}")
    else:
        logger.warning(f"Environment file {env_path} not found")

# Load environment variables on module import
load_env()

# Helper functions for getting environment variables with type conversion
def get_env(key: str, default: Any = None, cast: Optional[Type] = None) -> Any:
    """
    Get environment variable with optional type casting.
    
    Args:
        key: Environment variable name
        default: Default value if environment variable is not set
        cast: Type to cast the value to (int, float, bool, etc.)
        
    Returns:
        The environment variable value with appropriate type casting
    """
    value = os.environ.get(key, default)
    
    if value is None:
        return None
    
    if cast is None:
        return value
    
    if cast is bool:
        return str(value).lower() in ('true', 'yes', 'y', '1')
    
    return cast(value)

def get_int(key: str, default: Optional[int] = None) -> Optional[int]:
    """Get environment variable as integer."""
    return get_env(key, default, int)

def get_float(key: str, default: Optional[float] = None) -> Optional[float]:
    """Get environment variable as float."""
    return get_env(key, default, float)

def get_bool(key: str, default: Optional[bool] = None) -> Optional[bool]:
    """Get environment variable as boolean."""
    return get_env(key, default, bool)

def get_list(key: str, default: Optional[List] = None, delimiter: str = ',') -> Optional[List[str]]:
    """
    Get environment variable as list of strings.
    
    Args:
        key: Environment variable name
        default: Default value if environment variable is not set
        delimiter: Delimiter to split the string by
        
    Returns:
        List of strings
    """
    value = os.environ.get(key)
    if value is None:
        return default
    return [item.strip() for item in value.split(delimiter)]

def get_dict(key: str, default: Optional[Dict] = None, delimiter: str = ',', 
             pair_delimiter: str = ':') -> Optional[Dict[str, str]]:
    """
    Get environment variable as dictionary.
    
    Args:
        key: Environment variable name
        default: Default value if environment variable is not set
        delimiter: Delimiter to split the string by for items
        pair_delimiter: Delimiter to split key-value pairs
        
    Returns:
        Dictionary of key-value pairs
    """
    value = os.environ.get(key)
    if value is None:
        return default
    
    result = {}
    pairs = value.split(delimiter)
    for pair in pairs:
        if pair_delimiter in pair:
            k, v = pair.split(pair_delimiter, 1)
            result[k.strip()] = v.strip()
    
    return result
