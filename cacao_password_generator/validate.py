"""
Password validation functionality for cacao-password-generator.

This module provides password validation against configuration constraints,
returning detailed error messages for validation failures.
"""

from typing import Dict, Any, Optional, Tuple, List

from .config import load_config
from .utils import categorize_characters, validate_password_length, get_character_requirements


def validate(password: str, config: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[str]]:
    """
    Validate a password against configuration constraints.
    
    Args:
        password: Password string to validate
        config: Optional configuration dictionary. If None, uses defaults.
        
    Returns:
        Tuple of (is_valid, list_of_errors)
        - is_valid: True if password meets all requirements, False otherwise
        - list_of_errors: List of human-readable error messages (empty if valid)
    """
    if not isinstance(password, str):
        return False, ["Password must be a string"]
    
    # Check for empty password first
    if len(password) == 0:
        return False, ["Password cannot be empty."]
    
    # Load configuration
    final_config = load_config(config)
    
    errors = []
    
    # Validate length constraints first
    length_errors = _validate_length(password, final_config)
    errors.extend(length_errors)
    
    # For very short passwords (less than 4 chars), only report length errors
    # For longer passwords that are still too short, report both length and character errors
    if not length_errors or len(password) >= 4:
        char_errors = _validate_character_requirements(password, final_config)
        errors.extend(char_errors)
    
    is_valid = len(errors) == 0
    return is_valid, errors


def _validate_length(password: str, config: Dict[str, Any]) -> List[str]:
    """
    Validate password length against configuration.
    
    Args:
        password: Password to validate
        config: Configuration dictionary
        
    Returns:
        List of length-related error messages
    """
    errors = []
    length = len(password)
    min_length = config['minlen']
    max_length = config['maxlen']
    
    if length < min_length:
        errors.append(f"Password is too short. It must be at least {min_length} characters long, but only has {length} characters.")
    
    if length > max_length:
        errors.append(f"Password is too long. It cannot exceed {max_length} characters, but has {length} characters.")
    
    return errors


def _validate_character_requirements(password: str, config: Dict[str, Any]) -> List[str]:
    """
    Validate character requirements against configuration.
    
    Args:
        password: Password to validate
        config: Configuration dictionary
        
    Returns:
        List of character requirement error messages
    """
    errors = []
    char_counts = categorize_characters(password)
    requirements = get_character_requirements(config)
    
    # Check uppercase requirement
    if char_counts['uppercase'] < requirements['uppercase']:
        errors.append(
            f"Password needs at least {requirements['uppercase']} uppercase letter(s), "
            f"got: {char_counts['uppercase']}."
        )
    
    # Check lowercase requirement
    if char_counts['lowercase'] < requirements['lowercase']:
        errors.append(
            f"Password needs at least {requirements['lowercase']} lowercase letter(s), "
            f"got: {char_counts['lowercase']}."
        )
    
    # Check digits requirement
    if char_counts['digits'] < requirements['digits']:
        errors.append(
            f"Password needs at least {requirements['digits']} digit(s), "
            f"got: {char_counts['digits']}."
        )
    
    # Check special characters requirement
    if char_counts['special'] < requirements['special']:
        errors.append(
            f"Password needs at least {requirements['special']} special character(s), "
            f"got: {char_counts['special']}."
        )
    
    return errors


def validate_detailed(password: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Perform detailed password validation with comprehensive analysis.
    
    Args:
        password: Password string to validate
        config: Optional configuration dictionary
        
    Returns:
        Dictionary containing:
        - 'valid': bool indicating if password is valid
        - 'errors': list of error messages
        - 'analysis': detailed character analysis
        - 'requirements': configuration requirements
        - 'length_info': length validation details
    """
    final_config = load_config(config)
    is_valid, errors = validate(password, config)
    
    char_counts = categorize_characters(password)
    requirements = get_character_requirements(final_config)
    
    # Length analysis
    length = len(password)
    length_info = {
        'current': length,
        'minimum': final_config['minlen'],
        'maximum': final_config['maxlen'],
        'valid': final_config['minlen'] <= length <= final_config['maxlen']
    }
    
    # Character requirement analysis
    char_analysis = {}
    for char_type in ['uppercase', 'lowercase', 'digits', 'special']:
        char_analysis[char_type] = {
            'current': char_counts[char_type],
            'required': requirements[char_type],
            'valid': char_counts[char_type] >= requirements[char_type]
        }
    
    return {
        'valid': is_valid,
        'errors': errors,
        'analysis': char_analysis,
        'requirements': requirements,
        'length_info': length_info,
        'character_counts': char_counts
    }


def check_password_meets_minimum_requirements(password: str, 
                                            config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Quick check if password meets minimum requirements without detailed errors.
    
    Args:
        password: Password to validate
        config: Optional configuration dictionary
        
    Returns:
        True if password meets all minimum requirements, False otherwise
    """
    is_valid, _ = validate(password, config)
    return is_valid


def get_validation_summary(password: str, 
                         config: Optional[Dict[str, Any]] = None) -> str:
    """
    Get a human-readable summary of password validation.
    
    Args:
        password: Password to validate
        config: Optional configuration dictionary
        
    Returns:
        Human-readable validation summary string
    """
    is_valid, errors = validate(password, config)
    
    if is_valid:
        return "Password meets all requirements"
    else:
        error_count = len(errors)
        if error_count == 1:
            return f"Password has 1 issue: {errors[0]}"
        else:
            return f"Password has {error_count} issues: " + "; ".join(errors)


def validate_multiple(passwords: List[str], 
                     config: Optional[Dict[str, Any]] = None) -> List[Tuple[bool, List[str]]]:
    """
    Validate multiple passwords against the same configuration.
    
    Args:
        passwords: List of password strings to validate
        config: Optional configuration dictionary
        
    Returns:
        List of validation results, one for each password
    """
    return [validate(password, config) for password in passwords]