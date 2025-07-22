"""
Shared test fixtures and configuration for cacao-password-generator tests.

This module provides pytest fixtures that are used across multiple test modules
to ensure consistent test data and setup.
"""

import os
import pytest
import tempfile
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

# Import the package modules we're testing
import cacao_password_generator as cpg
from cacao_password_generator.config import get_default_config
from cacao_password_generator.utils import ALL_CHARS, UPPERCASE_CHARS, LOWERCASE_CHARS, DIGIT_CHARS, SPECIAL_CHARS


@pytest.fixture
def default_config():
    """Provide default configuration for tests."""
    return get_default_config()


@pytest.fixture
def custom_config():
    """Provide a custom configuration for testing."""
    return {
        'minlen': 8,
        'maxlen': 12,
        'minuchars': 2,
        'minlchars': 2,
        'minnumbers': 1,
        'minschars': 1
    }


@pytest.fixture
def strict_config():
    """Provide a strict configuration for testing edge cases."""
    return {
        'minlen': 16,
        'maxlen': 20,
        'minuchars': 4,
        'minlchars': 4,
        'minnumbers': 3,
        'minschars': 2
    }


@pytest.fixture
def minimal_config():
    """Provide minimal configuration for testing."""
    return {
        'minlen': 4,
        'maxlen': 6,
        'minuchars': 1,
        'minlchars': 1,
        'minnumbers': 0,
        'minschars': 0
    }


@pytest.fixture
def invalid_config():
    """Provide invalid configuration for testing error handling."""
    return {
        'minlen': 10,
        'maxlen': 8,  # Invalid: max < min
        'minuchars': 2,
        'minlchars': 2,
        'minnumbers': 1,
        'minschars': 1
    }


@pytest.fixture
def test_passwords():
    """Provide various test passwords for validation and rating tests."""
    return {
        'weak': [
            '123',
            'abc',
            'password',
            'ABCDEFG',
            '1234567'
        ],
        'medium': [
            'Password1',
            'MyPass123',
            'Test@123',
            'Secure99'
        ],
        'strong': [
            'MySecureP@ssw0rd!',
            'Complex#Password123',
            'Str0ng&Secure!Pass',
            'Test!ng#Strong2023'
        ],
        'excellent': [
            'MyS3cur3P@ssw0rd!2023',
            'C0mpl3x&V3ryStr0ng!P@ss',
            'Exc3ll3nt#S3cur1ty!K3y$2024',
            'Ultr@S3cur3!C0mpl3x&P@ssw0rd#'
        ]
    }


@pytest.fixture
def validation_test_cases():
    """Provide test cases for password validation."""
    return [
        # (password, expected_valid, description)
        ('Abc123!', True, 'Valid password with all character types'),
        ('abc', False, 'Too short, missing uppercase/numbers/special chars'),
        ('ABCDEFGHIJ', False, 'Missing lowercase/numbers/special chars'),
        ('password123', False, 'Missing uppercase/special chars'),
        ('PASSWORD123!', False, 'Missing lowercase chars'),
        ('MyPassword', False, 'Missing numbers/special chars'),
        ('MyPassword123', False, 'Missing special chars'),
        ('MyPassword!', False, 'Missing numbers'),
        ('', False, 'Empty password'),
        ('A1!', False, 'Too short even with all char types')
    ]


@pytest.fixture
def character_sets():
    """Provide character sets for testing."""
    return {
        'uppercase': UPPERCASE_CHARS,
        'lowercase': LOWERCASE_CHARS,
        'digits': DIGIT_CHARS,
        'special': SPECIAL_CHARS,
        'all': ALL_CHARS
    }


@pytest.fixture
def mock_env():
    """Provide mock environment variables for testing."""
    env_vars = {
        'CACAO_MIN_LENGTH': '8',
        'CACAO_MAX_LENGTH': '16',
        'CACAO_MIN_UPPERCASE': '2',
        'CACAO_MIN_LOWERCASE': '2',
        'CACAO_MIN_NUMBERS': '1',
        'CACAO_MIN_SPECIAL': '1',
        'CACAO_ALLOW_SYMBOLS': 'true',
        'CACAO_ALLOW_SPACES': 'false'
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def cli_command():
    """Provide CLI command for subprocess testing."""
    import sys
    
    # Use the module execution approach for testing
    return [sys.executable, '-m', 'cacao_password_generator.cli']


@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file for testing."""
    config_content = """
# Test configuration file
minlen = 10
maxlen = 15
minuchars = 2
minlchars = 3
minnumbers = 2
minschars = 1
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
        f.write(config_content)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    try:
        os.unlink(temp_file)
    except OSError:
        pass


@pytest.fixture
def cli_runner():
    """Provide a CLI runner for testing command line interface."""
    import subprocess
    import sys
    
    def run_cli(args: List[str], timeout: int = 10):
        """Run CLI command and return result."""
        cmd = [sys.executable, '-m', 'cacao_password_generator.cli'] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)
    
    return run_cli


@pytest.fixture
def sample_generated_passwords():
    """Generate sample passwords for testing."""
    passwords = []
    configs = [
        None,  # Default config
        {'minlen': 8, 'maxlen': 10},
        {'minlen': 12, 'maxlen': 16, 'minuchars': 3},
        {'minlen': 6, 'maxlen': 8, 'minschars': 0}
    ]
    
    for config in configs:
        for _ in range(3):  # Generate 3 passwords for each config
            pwd = cpg.generate(config)
            passwords.append((pwd, config))
    
    return passwords


@pytest.fixture
def parametrized_configs():
    """Provide parametrized configurations for comprehensive testing."""
    return [
        # (config_name, config_dict)
        ('default', None),
        ('minimal', {
            'minlen': 4, 'maxlen': 6, 'minuchars': 1, 'minlchars': 1,
            'minnumbers': 0, 'minschars': 0
        }),
        ('balanced', {
            'minlen': 8, 'maxlen': 12, 'minuchars': 2, 'minlchars': 2,
            'minnumbers': 1, 'minschars': 1
        }),
        ('strict', {
            'minlen': 12, 'maxlen': 16, 'minuchars': 3, 'minlchars': 3,
            'minnumbers': 2, 'minschars': 2
        }),
        ('no_symbols', {
            'minlen': 8, 'maxlen': 10, 'minuchars': 2, 'minlchars': 2,
            'minnumbers': 1, 'minschars': 0
        })
    ]


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables before each test."""
    # Store original environment
    original_env = os.environ.copy()
    
    # Remove any cacao-related environment variables
    cacao_vars = [k for k in os.environ.keys() if k.startswith('CACAO_')]
    for var in cacao_vars:
        os.environ.pop(var, None)
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_secrets():
    """Mock secrets module for deterministic testing when needed."""
    with patch('cacao_password_generator.core.secrets') as mock_secrets:
        # Set up deterministic behavior
        mock_secrets.choice.side_effect = lambda seq: seq[0] if seq else ''
        mock_secrets.randbelow.side_effect = lambda n: 0 if n > 0 else 0
        yield mock_secrets


# Performance testing fixtures
@pytest.fixture
def performance_config():
    """Configuration for performance testing."""
    return {
        'generation_counts': [1, 10, 100, 1000],
        'length_ranges': [(6, 8), (10, 12), (16, 20), (24, 32)],
        'complexity_levels': [
            {'minuchars': 1, 'minlchars': 1, 'minnumbers': 0, 'minschars': 0},
            {'minuchars': 2, 'minlchars': 2, 'minnumbers': 1, 'minschars': 1},
            {'minuchars': 4, 'minlchars': 4, 'minnumbers': 2, 'minschars': 2}
        ]
    }


# Markers for different test categories
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (may take longer to run)"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "cli: marks tests as CLI tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security-related"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )