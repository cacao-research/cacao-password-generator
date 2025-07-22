# Testing Documentation

## Overview

This document provides comprehensive instructions for running the test suite for the cacao-password-generator package. The test suite is built using pytest and includes unit tests, integration tests, CLI tests, and performance tests with coverage reporting.

## Prerequisites

### Installing Test Dependencies

To run the tests, you need to install the development dependencies:

```bash
# Install the package in development mode with test dependencies
pip install -e ".[dev]"

# Or install just the test dependencies
pip install pytest>=7.0 pytest-cov>=4.0
```

### Python Version Requirements

- Python 3.8 or higher
- All tests are compatible with Python 3.8-3.12

## Test Structure

The test suite is organized into the following modules:

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py             # Shared fixtures and configuration
├── test_core.py            # Core password generation functionality
├── test_config.py          # Configuration management tests
├── test_validate.py        # Password validation tests
├── test_rating.py          # Password strength rating tests
├── test_cli.py             # Command-line interface tests
├── test_utils.py           # Utility functions tests
├── test_integration.py     # End-to-end integration tests
├── test_basic_functionality.py  # Legacy basic functionality tests
└── test_cli_functionality.py    # Legacy CLI functionality tests
```

## Running Tests

### Basic Test Execution

Run all tests:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

Run tests with coverage reporting:
```bash
pytest --cov=cacao_password_generator --cov-report=term-missing
```

### Test Categories and Markers

The test suite uses markers to categorize different types of tests:

#### Available Markers

- `slow`: Tests that may take several seconds to complete
- `integration`: End-to-end integration tests
- `cli`: Tests that specifically test CLI functionality
- `performance`: Tests that measure performance characteristics

#### Running Specific Test Categories

Run only fast tests (exclude slow tests):
```bash
pytest -m "not slow"
```

Run only integration tests:
```bash
pytest -m integration
```

Run only CLI tests:
```bash
pytest -m cli
```

Run performance tests:
```bash
pytest -m performance
```

Combine markers (run integration tests but not slow ones):
```bash
pytest -m "integration and not slow"
```

### Running Specific Test Files

Run tests from a specific file:
```bash
pytest tests/test_core.py
```

Run tests from multiple files:
```bash
pytest tests/test_core.py tests/test_validate.py
```

### Running Specific Test Functions or Classes

Run a specific test function:
```bash
pytest tests/test_core.py::test_generate_basic_password
```

Run a specific test class:
```bash
pytest tests/test_core.py::TestPasswordGeneration
```

Run a specific test method:
```bash
pytest tests/test_core.py::TestPasswordGeneration::test_generate_basic_password
```

## Coverage Reporting

### Generating Coverage Reports

The test configuration automatically generates coverage reports when using the `--cov` flag:

```bash
# Generate terminal coverage report
pytest --cov=cacao_password_generator --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=cacao_password_generator --cov-report=html

# Generate XML coverage report (for CI/CD)
pytest --cov=cacao_password_generator --cov-report=xml
```

### Coverage Report Formats

1. **Terminal Report** (`--cov-report=term-missing`): Shows coverage in the terminal with missing lines
2. **HTML Report** (`--cov-report=html`): Creates an interactive HTML report in `htmlcov/` directory
3. **XML Report** (`--cov-report=xml`): Creates `coverage.xml` for CI/CD integration

### Viewing HTML Coverage Report

After generating an HTML report:
```bash
# Open the coverage report in your browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Test Configuration

### pytest Configuration

The test configuration is defined in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = [
    "-ra",                    # Show all test results
    "--strict-markers",       # Treat unknown markers as errors
    "--strict-config",        # Treat config warnings as errors
    "--cov=cacao_password_generator",  # Enable coverage
    "--cov-branch",           # Include branch coverage
    "--cov-report=term-missing:skip-covered",  # Terminal report
    "--cov-report=html:htmlcov",  # HTML report
    "--cov-report=xml",       # XML report
]
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow (may take several seconds)",
    "integration: marks tests as integration tests",
    "cli: marks tests that test CLI functionality", 
    "performance: marks tests that test performance characteristics",
]
```

### Coverage Configuration

Coverage settings are also in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["cacao_password_generator"]
omit = ["*/tests/*", "*/test_*.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if __name__ == .__main__.:",
    # ... other exclusions
]
```

## Advanced Testing Scenarios

### Testing with Environment Variables

Some tests verify environment variable behavior:

```bash
# Test with environment variables set
CACAO_PW_MINLEN=12 CACAO_PW_MAXLEN=20 pytest tests/test_config.py

# Test CLI with environment variables
CACAO_PW_MINLEN=16 pytest tests/test_cli.py::TestCLIIntegration::test_cli_basic_generation
```

### Parallel Test Execution

Install pytest-xdist for parallel execution:
```bash
pip install pytest-xdist

# Run tests in parallel
pytest -n auto  # Use all available CPU cores
pytest -n 4     # Use 4 parallel workers
```

### Testing with Different Python Versions

Using tox (if available):
```bash
pip install tox
tox  # Test against all configured Python versions
```

Using pyenv to test specific versions:
```bash
pyenv local 3.8.10 3.9.7 3.10.4 3.11.1
python3.8 -m pytest
python3.9 -m pytest
# ... etc
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    
    - name: Run tests
      run: pytest
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Test Development Guidelines

### Writing New Tests

1. **Test File Naming**: Use `test_*.py` pattern
2. **Test Function Naming**: Use `test_*` pattern
3. **Test Class Naming**: Use `Test*` pattern
4. **Fixtures**: Place shared fixtures in `conftest.py`
5. **Markers**: Use appropriate markers for test categorization

### Example Test Structure

```python
import pytest
from cacao_password_generator import generate

class TestPasswordGeneration:
    """Test password generation functionality."""
    
    def test_basic_generation(self):
        """Test basic password generation."""
        password = generate()
        assert isinstance(password, str)
        assert len(password) >= 8
    
    @pytest.mark.slow
    def test_bulk_generation_performance(self):
        """Test performance of bulk generation."""
        passwords = [generate() for _ in range(1000)]
        assert len(passwords) == 1000
    
    @pytest.mark.integration
    def test_end_to_end_workflow(self):
        """Test complete generation and validation workflow."""
        password = generate()
        from cacao_password_generator import validate
        is_valid, errors = validate(password)
        assert is_valid
```

### Test Data and Fixtures

Use fixtures for common test data:

```python
@pytest.fixture
def sample_config():
    """Provide a sample configuration for testing."""
    return {
        'minlen': 12,
        'maxlen': 16,
        'minuchars': 2,
        'minnumbers': 1
    }

def test_with_config(sample_config):
    password = generate(sample_config)
    assert len(password) >= 12
```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure package is installed in development mode
pip install -e .
```

#### CLI Tests Failing
```bash
# Ensure the CLI script is properly installed
pip install -e .
which cacao-pass  # Should show the installed script
```

#### Coverage Not Working
```bash
# Install coverage dependencies
pip install pytest-cov

# Check coverage configuration in pyproject.toml
```

#### Slow Tests Timing Out
```bash
# Skip slow tests during development
pytest -m "not slow"

# Or increase timeout (if using pytest-timeout)
pytest --timeout=300
```

### Performance Considerations

- **Fast Tests**: Most tests should complete in <1 second
- **Slow Tests**: Marked with `@pytest.mark.slow`, may take 1-10 seconds
- **Performance Tests**: Marked with `@pytest.mark.performance`, verify timing constraints

### Debug Mode

Run tests in debug mode with more verbose output:
```bash
pytest -vv --tb=long --capture=no
```

Add print debugging (temporarily):
```python
def test_debug_example():
    password = generate()
    print(f"Generated password: {password}")  # Will show with --capture=no
    assert len(password) >= 8
```

## Expected Coverage

The test suite aims for:
- **Overall Coverage**: >95%
- **Branch Coverage**: >90%
- **Critical Modules**: 100% (core.py, validate.py, rating.py)

Current coverage should be verified by running:
```bash
pytest --cov=cacao_password_generator --cov-report=term-missing
```

## Integration with Development Workflow

### Pre-commit Testing

Add to your development workflow:
```bash
# Quick test run before committing
pytest -m "not slow"

# Full test run before pushing
pytest
```

### IDE Integration

Most IDEs support pytest integration:
- **VS Code**: Install Python extension, configure test discovery
- **PyCharm**: Built-in pytest support
- **Vim/Emacs**: Use appropriate plugins

## Summary

This comprehensive test suite ensures the reliability, security, and performance of the cacao-password-generator package. Regular execution of these tests helps maintain code quality and prevents regressions during development.

For questions or issues with testing, please refer to the project's issue tracker or documentation.