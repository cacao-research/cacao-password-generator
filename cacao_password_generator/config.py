"""
Configuration management for cacao-password-generator.

This module provides configuration management with support for defaults,
environment variables, and runtime overrides.
"""

import os
from typing import Dict, Any, Optional


# Default configuration values
DEFAULT_CONFIG: Dict[str, Any] = {
    'minlen': 6,
    'maxlen': 16,
    'minuchars': 1,  # minimum uppercase characters
    'minlchars': 1,  # minimum lowercase characters
    'minnumbers': 1,  # minimum numbers
    'minschars': 1,  # minimum special characters
}

# Environment variable prefix
ENV_PREFIX = 'CACAO_PW_'

# Valid configuration keys
VALID_CONFIG_KEYS = set(DEFAULT_CONFIG.keys())


def load_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Load configuration from multiple sources with precedence:
    1. Runtime config parameter (highest priority)
    2. Environment variables
    3. Default values (lowest priority)
    
    Args:
        config: Optional runtime configuration overrides
        
    Returns:
        Merged configuration dictionary
        
    Raises:
        ValueError: If invalid configuration keys are provided
    """
    # Start with default configuration
    merged_config = DEFAULT_CONFIG.copy()
    
    # Override with environment variables
    for key in DEFAULT_CONFIG:
        env_key = f"{ENV_PREFIX}{key.upper()}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            try:
                # Convert environment variable to appropriate type
                merged_config[key] = int(env_value)
            except ValueError:
                raise ValueError(f"Invalid value for {env_key}: {env_value}. Must be an integer.")
    
    # Override with runtime configuration
    if config:
        # Validate configuration keys
        invalid_keys = set(config.keys()) - VALID_CONFIG_KEYS
        if invalid_keys:
            raise ValueError(f"Invalid configuration keys: {invalid_keys}. "
                           f"Valid keys are: {VALID_CONFIG_KEYS}")
        
        # Validate configuration values
        for key, value in config.items():
            if not isinstance(value, int):
                raise ValueError(f"Configuration value for '{key}' must be an integer, got: {value}")
            # Allow negative values for exclusion (CLI --no-* options use -1)
            if value < -1:
                raise ValueError(f"Configuration value for '{key}' must be >= -1, got: {value}")
        
        merged_config.update(config)
    
    # Validate final configuration
    _validate_config(merged_config)
    
    return merged_config


def _validate_config(config: Dict[str, Any]) -> None:
    """
    Validate the final configuration for logical consistency.
    
    Args:
        config: Configuration dictionary to validate
        
    Raises:
        ValueError: If configuration is invalid
    """
    # Check that minlen <= maxlen
    if config['minlen'] > config['maxlen']:
        raise ValueError(f"minlen ({config['minlen']}) cannot be greater than maxlen ({config['maxlen']})")
    
    # Check that minimum character requirements don't exceed maximum length
    min_chars_required = (
        config['minuchars'] + 
        config['minlchars'] + 
        config['minnumbers'] + 
        config['minschars']
    )
    
    if min_chars_required > config['maxlen']:
        raise ValueError(
            f"Sum of minimum character requirements ({min_chars_required}) "
            f"cannot exceed maxlen ({config['maxlen']})"
        )
    
    # Check that minimum character requirements allow for minimum length
    if min_chars_required > config['minlen'] and config['minlen'] < min_chars_required:
        # This is a warning case - we'll allow it but the generator will use minlen
        pass


def get_default_config() -> Dict[str, Any]:
    """
    Get the default configuration values.
    
    Returns:
        Copy of default configuration dictionary
    """
    return DEFAULT_CONFIG.copy()


def get_config_from_env() -> Dict[str, Any]:
    """
    Get configuration from environment variables only.
    
    Returns:
        Configuration dictionary with values from environment variables,
        falling back to defaults for unset variables
    """
    return load_config()