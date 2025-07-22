"""
Utility functions and constants for cacao-password-generator.

This module provides shared utilities, character sets, and helper functions
used across the password generation, validation, and rating modules.
"""

import string
import math
from typing import Set, Dict, Any


# Character sets
UPPERCASE_CHARS = set(string.ascii_uppercase)
LOWERCASE_CHARS = set(string.ascii_lowercase)
DIGIT_CHARS = set(string.digits)
SPECIAL_CHARS = set("!@#$%^&*()_+-=[]{}|;:,.<>")

# All available character sets
ALL_CHAR_SETS = {
    'uppercase': UPPERCASE_CHARS,
    'lowercase': LOWERCASE_CHARS,
    'digits': DIGIT_CHARS,
    'special': SPECIAL_CHARS
}

# Combined character set for password generation
ALL_CHARS = UPPERCASE_CHARS | LOWERCASE_CHARS | DIGIT_CHARS | SPECIAL_CHARS


def categorize_characters(password: str) -> Dict[str, int]:
    """
    Categorize characters in a password and count them by type.
    
    Args:
        password: Password string to analyze
        
    Returns:
        Dictionary with counts for each character type:
        - 'uppercase': count of uppercase letters
        - 'lowercase': count of lowercase letters  
        - 'digits': count of digits
        - 'special': count of special characters
        - 'other': count of characters not in standard sets
    """
    counts = {
        'uppercase': 0,
        'lowercase': 0,
        'digits': 0,
        'special': 0,
        'other': 0
    }
    
    for char in password:
        if char in UPPERCASE_CHARS:
            counts['uppercase'] += 1
        elif char in LOWERCASE_CHARS:
            counts['lowercase'] += 1
        elif char in DIGIT_CHARS:
            counts['digits'] += 1
        elif char in SPECIAL_CHARS:
            counts['special'] += 1
        else:
            counts['other'] += 1
    
    return counts


def get_character_space_size(char_counts: Dict[str, int]) -> int:
    """
    Calculate the character space size based on character types present.
    
    Args:
        char_counts: Dictionary of character type counts from categorize_characters()
        
    Returns:
        Total size of character space (alphabet size)
    """
    space_size = 0
    
    if char_counts['uppercase'] > 0:
        space_size += len(UPPERCASE_CHARS)
    if char_counts['lowercase'] > 0:
        space_size += len(LOWERCASE_CHARS)
    if char_counts['digits'] > 0:
        space_size += len(DIGIT_CHARS)
    if char_counts['special'] > 0:
        space_size += len(SPECIAL_CHARS)
    if char_counts['other'] > 0:
        # Approximate for non-standard characters
        space_size += 10
    
    return space_size


def calculate_entropy(password: str) -> float:
    """
    Calculate the entropy (in bits) of a password.
    
    Entropy is calculated as: log2(alphabet_size) * password_length
    
    Args:
        password: Password string to analyze
        
    Returns:
        Entropy in bits as a float
    """
    if not password:
        return 0.0
    
    char_counts = categorize_characters(password)
    alphabet_size = get_character_space_size(char_counts)
    
    if alphabet_size == 0:
        return 0.0
    
    return math.log2(alphabet_size) * len(password)


def get_required_chars_for_config(config: Dict[str, Any]) -> Dict[str, Set[str]]:
    """
    Get the required character sets based on configuration.
    
    Args:
        config: Configuration dictionary with minimum character requirements
        
    Returns:
        Dictionary mapping requirement types to their character sets
    """
    required_sets = {}
    
    if config.get('minuchars', 0) > 0:
        required_sets['uppercase'] = UPPERCASE_CHARS
    if config.get('minlchars', 0) > 0:
        required_sets['lowercase'] = LOWERCASE_CHARS
    if config.get('minnumbers', 0) > 0:
        required_sets['digits'] = DIGIT_CHARS
    if config.get('minschars', 0) > 0:
        required_sets['special'] = SPECIAL_CHARS
    
    return required_sets


def get_available_chars_for_config(config: Dict[str, Any]) -> Set[str]:
    """
    Get all available characters for password generation based on configuration.
    
    Character types are included unless explicitly excluded:
    - Negative minimum values indicate exclusion (used by CLI --no-* options)
    - Zero or positive values allow the character type
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Set of all characters that can be used for password generation
    """
    available_chars = set()
    
    # Include each character type unless explicitly excluded (negative value)
    # Default behavior is to include all character types
    
    # Check if uppercase should be included (default: yes, exclude if < 0)
    if config.get('minuchars', 1) >= 0:
        available_chars.update(UPPERCASE_CHARS)
    
    # Check if lowercase should be included (default: yes, exclude if < 0)
    if config.get('minlchars', 1) >= 0:
        available_chars.update(LOWERCASE_CHARS)
    
    # Check if digits should be included (default: yes, exclude if < 0)
    if config.get('minnumbers', 1) >= 0:
        available_chars.update(DIGIT_CHARS)
    
    # Check if special characters should be included (default: yes, exclude if < 0)
    if config.get('minschars', 1) >= 0:
        available_chars.update(SPECIAL_CHARS)
    
    # Ensure we always have at least some characters available
    if not available_chars:
        # Fall back to at least lowercase letters to avoid empty set
        available_chars.update(LOWERCASE_CHARS)
    
    return available_chars


def validate_password_length(password: str, config: Dict[str, Any]) -> bool:
    """
    Validate if password length meets configuration requirements.
    
    Args:
        password: Password to validate
        config: Configuration dictionary with minlen and maxlen
        
    Returns:
        True if length is valid, False otherwise
    """
    length = len(password)
    return config.get('minlen', 0) <= length <= config.get('maxlen', float('inf'))


def get_character_requirements(config: Dict[str, Any]) -> Dict[str, int]:
    """
    Extract character requirements from configuration.
    
    Negative values (used for exclusion) are converted to 0 for generation purposes.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary with minimum requirements for each character type
    """
    return {
        'uppercase': max(0, config.get('minuchars', 0)),
        'lowercase': max(0, config.get('minlchars', 0)),
        'digits': max(0, config.get('minnumbers', 0)),
        'special': max(0, config.get('minschars', 0))
    }