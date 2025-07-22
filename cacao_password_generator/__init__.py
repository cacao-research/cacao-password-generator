"""
Cacao Password Generator - A secure password generator with configurable constraints.

This package provides secure password generation using Python's secrets module,
with configurable constraints, password validation, and strength rating.

Main API Functions:
    generate() - Generate secure passwords with configurable constraints
    validate() - Validate passwords against configuration requirements
    rating() - Rate password strength (weak/medium/strong/excellent)

Example Usage:
    >>> import cacao_password_generator as cpg
    >>> 
    >>> # Generate a password with default settings
    >>> password = cpg.generate()
    >>> 
    >>> # Generate with custom length
    >>> long_password = cpg.generate(length=20)
    >>> 
    >>> # Generate with custom configuration
    >>> config = {'minlen': 10, 'maxlen': 15, 'minuchars': 2}
    >>> custom_password = cpg.generate(config)
    >>> 
    >>> # Validate a password
    >>> is_valid, errors = cpg.validate("MyPassword123!")
    >>> 
    >>> # Rate password strength
    >>> strength = cpg.rating("MyPassword123!")  # Returns: "strong"
"""

from .core import generate, generate_multiple
from .validate import validate, validate_detailed, check_password_meets_minimum_requirements
from .rating import rating, detailed_rating, rate_password_strength
from .config import load_config, get_default_config

# Package metadata
__version__ = "1.0.0"
__author__ = "Cacao Password Generator Contributors"
__license__ = "MIT"
__description__ = "A secure password generator with configurable constraints and strength rating"

# Main API exports - these are the primary functions users should use
__all__ = [
    # Core password generation
    "generate",
    "generate_multiple",
    
    # Password validation
    "validate", 
    "validate_detailed",
    "check_password_meets_minimum_requirements",
    
    # Password strength rating
    "rating",
    "detailed_rating",
    "rate_password_strength",
    
    # Configuration management
    "load_config",
    "get_default_config",
    
    # Package metadata
    "__version__",
    "__author__", 
    "__license__",
    "__description__"
]


def get_version() -> str:
    """
    Get the package version.
    
    Returns:
        Version string
    """
    return __version__


def get_package_info() -> dict:
    """
    Get comprehensive package information.
    
    Returns:
        Dictionary with package metadata and default configuration
    """
    return {
        "name": "cacao-password-generator",
        "version": __version__,
        "description": __description__,
        "author": __author__,
        "license": __license__,
        "default_config": get_default_config(),
        "api_functions": [
            "generate(config=None, *, length=None)",
            "validate(password, config=None)", 
            "rating(password)"
        ]
    }


# Convenience function for quick password generation and analysis
def quick_analysis(password: str = None, config: dict = None) -> dict:
    """
    Perform quick password generation and analysis.
    
    If no password is provided, generates one first.
    
    Args:
        password: Password to analyze. If None, generates a new one.
        config: Optional configuration for generation/validation
        
    Returns:
        Dictionary with generation, validation, and rating results
    """
    if password is None:
        password = generate(config)
        generated = True
    else:
        generated = False
    
    # Validate the password
    is_valid, errors = validate(password, config)
    
    # Rate the password
    strength_rating = rating(password)
    
    return {
        "password": password,
        "generated": generated,
        "valid": is_valid,
        "errors": errors,
        "rating": strength_rating,
        "length": len(password)
    }


# Add quick_analysis to exports
__all__.append("quick_analysis")


# Package-level constants for easy access
DEFAULT_MIN_LENGTH = 6
DEFAULT_MAX_LENGTH = 16
SUPPORTED_RATINGS = ["weak", "medium", "strong", "excellent"]

__all__.extend([
    "DEFAULT_MIN_LENGTH",
    "DEFAULT_MAX_LENGTH", 
    "SUPPORTED_RATINGS"
])