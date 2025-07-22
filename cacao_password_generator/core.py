"""
Core password generation functionality for cacao-password-generator.

This module provides secure password generation using Python's secrets module
with configurable constraints and character requirements.
"""

import secrets
from typing import Dict, Any, Optional, List, Set

from .config import load_config
from .utils import (
    ALL_CHARS, UPPERCASE_CHARS, LOWERCASE_CHARS, DIGIT_CHARS, SPECIAL_CHARS,
    get_required_chars_for_config, get_available_chars_for_config,
    get_character_requirements
)


def generate(config: Optional[Dict[str, Any]] = None, *, length: Optional[int] = None) -> str:
    """
    Generate a secure password using Python's secrets module.
    
    Args:
        config: Optional configuration dictionary. If None, uses defaults.
        length: Optional length override. If provided, overrides config length constraints.
               Must be positive integer.
    
    Returns:
        Cryptographically secure random password as string
        
    Raises:
        ValueError: If length parameter is invalid or configuration is invalid
    """
    # Load and validate configuration
    final_config = load_config(config)
    
    # Handle length parameter
    if length is not None:
        if not isinstance(length, int) or length <= 0:
            raise ValueError(f"Length must be a positive integer, got: {length}")
        
        # Override config with specific length
        target_length = length
        
        # Check if length allows meeting minimum character requirements
        char_requirements = get_character_requirements(final_config)
        min_chars_needed = sum(char_requirements.values())
        
        if length < min_chars_needed:
            raise ValueError(
                f"Length {length} is too short to meet minimum character requirements "
                f"(need at least {min_chars_needed} characters)"
            )
    else:
        # Use config length constraints
        min_length = final_config['minlen']
        max_length = final_config['maxlen']
        
        # Choose random length within range
        target_length = secrets.randbelow(max_length - min_length + 1) + min_length
    
    # Generate password that meets all requirements
    password = _generate_password_with_requirements(final_config, target_length)
    
    return password


def _generate_password_with_requirements(config: Dict[str, Any], length: int) -> str:
    """
    Generate password that meets all character requirements.
    
    Args:
        config: Validated configuration dictionary
        length: Target password length
        
    Returns:
        Password string meeting all requirements
    """
    char_requirements = get_character_requirements(config)
    available_chars = get_available_chars_for_config(config)
    
    # Step 1: Ensure minimum character requirements are met
    required_chars = []
    
    # Add required uppercase characters
    if char_requirements['uppercase'] > 0:
        required_chars.extend(
            _select_random_chars(UPPERCASE_CHARS, char_requirements['uppercase'])
        )
    
    # Add required lowercase characters
    if char_requirements['lowercase'] > 0:
        required_chars.extend(
            _select_random_chars(LOWERCASE_CHARS, char_requirements['lowercase'])
        )
    
    # Add required digit characters
    if char_requirements['digits'] > 0:
        required_chars.extend(
            _select_random_chars(DIGIT_CHARS, char_requirements['digits'])
        )
    
    # Add required special characters
    if char_requirements['special'] > 0:
        required_chars.extend(
            _select_random_chars(SPECIAL_CHARS, char_requirements['special'])
        )
    
    # Step 2: Fill remaining positions with random characters
    remaining_length = length - len(required_chars)
    
    if remaining_length > 0:
        additional_chars = _select_random_chars(available_chars, remaining_length)
        required_chars.extend(additional_chars)
    
    # Step 3: Shuffle the password to avoid predictable patterns
    password_list = required_chars
    _shuffle_list(password_list)
    
    return ''.join(password_list)


def _select_random_chars(char_set: Set[str], count: int) -> List[str]:
    """
    Select random characters from a character set.
    
    Args:
        char_set: Set of available characters
        count: Number of characters to select
        
    Returns:
        List of randomly selected characters
    """
    char_list = list(char_set)
    return [secrets.choice(char_list) for _ in range(count)]


def _shuffle_list(items: List[str]) -> None:
    """
    Cryptographically secure in-place shuffle of list items.
    
    Uses Fisher-Yates shuffle algorithm with secrets.randbelow()
    for cryptographic security.
    
    Args:
        items: List to shuffle in-place
    """
    for i in range(len(items) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        items[i], items[j] = items[j], items[i]


def generate_multiple(count: int, config: Optional[Dict[str, Any]] = None, 
                     *, length: Optional[int] = None) -> List[str]:
    """
    Generate multiple secure passwords.
    
    Args:
        count: Number of passwords to generate (must be positive)
        config: Optional configuration dictionary
        length: Optional length override for all passwords
        
    Returns:
        List of generated passwords
        
    Raises:
        ValueError: If count is not positive
    """
    if not isinstance(count, int) or count <= 0:
        raise ValueError(f"Count must be a positive integer, got: {count}")
    
    return [generate(config, length=length) for _ in range(count)]


def get_password_character_distribution(password: str) -> Dict[str, int]:
    """
    Analyze the character distribution of a generated password.
    
    Args:
        password: Password to analyze
        
    Returns:
        Dictionary with character type counts
    """
    from .utils import categorize_characters
    return categorize_characters(password)


def estimate_generation_time(config: Optional[Dict[str, Any]] = None) -> str:
    """
    Estimate the time complexity for password generation.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Human-readable string describing generation complexity
    """
    final_config = load_config(config)
    char_requirements = get_character_requirements(final_config)
    min_chars_needed = sum(char_requirements.values())
    
    if min_chars_needed == 0:
        return "Very fast (no character requirements)"
    elif min_chars_needed <= 4:
        return "Fast (minimal requirements)"
    elif min_chars_needed <= 8:
        return "Moderate (balanced requirements)"
    else:
        return "Slower (strict requirements)"