#!/usr/bin/env python3
"""
Test script to verify CLI functionality for cacao-password-generator.

This script tests the command-line interface comprehensively to ensure
all options work correctly and integrate properly with the core functionality.
"""

import subprocess
import sys
import re
from typing import List, Tuple


def run_cli_command(args: List[str]) -> Tuple[int, str, str]:
    """
    Run a CLI command and return results.
    
    Args:
        args: Command line arguments (excluding 'python -m')
        
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    cmd = [sys.executable, '-m', 'cacao_password_generator.cli'] + args
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def test_basic_generation():
    """Test basic password generation without arguments."""
    print("Testing basic password generation...")
    
    returncode, stdout, stderr = run_cli_command([])
    
    if returncode != 0:
        print(f"❌ FAILED: Basic generation failed with code {returncode}")
        print(f"   stderr: {stderr}")
        return False
    
    if not stdout.strip():
        print("❌ FAILED: No output generated")
        return False
    
    # Check for expected output pattern
    if "Generated Password:" not in stdout:
        print("❌ FAILED: Expected 'Generated Password:' in output")
        print(f"   stdout: {stdout}")
        return False
    
    if "Strength Rating:" not in stdout:
        print("❌ FAILED: Expected 'Strength Rating:' in output")
        print(f"   stdout: {stdout}")
        return False
    
    print("✅ PASSED: Basic generation works")
    return True


def test_version():
    """Test version display."""
    print("Testing version display...")
    
    returncode, stdout, stderr = run_cli_command(['--version'])
    
    if returncode != 0:
        print(f"❌ FAILED: Version command failed with code {returncode}")
        return False
    
    if "cacao-pass" not in stdout and "cacao-pass" not in stderr:
        print("❌ FAILED: Expected 'cacao-pass' in version output")
        print(f"   stdout: {stdout}")
        print(f"   stderr: {stderr}")
        return False
    
    print("✅ PASSED: Version display works")
    return True


def test_help():
    """Test help display."""
    print("Testing help display...")
    
    returncode, stdout, stderr = run_cli_command(['--help'])
    
    if returncode != 0:
        print(f"❌ FAILED: Help command failed with code {returncode}")
        return False
    
    help_output = stdout + stderr
    expected_sections = [
        "usage:",
        "Generate secure passwords",
        "Password Generation Options",
        "Length Constraints",
        "Character Requirements"
    ]
    
    for section in expected_sections:
        if section not in help_output:
            print(f"❌ FAILED: Expected '{section}' in help output")
            return False
    
    print("✅ PASSED: Help display works")
    return True


def test_length_override():
    """Test length parameter."""
    print("Testing length override...")
    
    returncode, stdout, stderr = run_cli_command(['--length', '20', '--quiet'])
    
    if returncode != 0:
        print(f"❌ FAILED: Length override failed with code {returncode}")
        print(f"   stderr: {stderr}")
        return False
    
    password = stdout.strip()
    if len(password) != 20:
        print(f"❌ FAILED: Expected 20 characters, got {len(password)}")
        print(f"   password: '{password}'")
        return False
    
    print("✅ PASSED: Length override works")
    return True


def test_quiet_mode():
    """Test quiet output mode."""
    print("Testing quiet mode...")
    
    returncode, stdout, stderr = run_cli_command(['--quiet'])
    
    if returncode != 0:
        print(f"❌ FAILED: Quiet mode failed with code {returncode}")
        print(f"   stderr: {stderr}")
        return False
    
    lines = stdout.strip().split('\n')
    if len(lines) != 1:
        print(f"❌ FAILED: Expected single line output, got {len(lines)} lines")
        print(f"   stdout: '{stdout}'")
        return False
    
    # Should just be the password
    password = lines[0]
    if len(password) < 6:  # Default minimum length
        print(f"❌ FAILED: Password too short: '{password}'")
        return False
    
    print("✅ PASSED: Quiet mode works")
    return True


def test_no_symbols():
    """Test symbol exclusion."""
    print("Testing symbol exclusion...")
    
    returncode, stdout, stderr = run_cli_command(['--no-symbols', '--quiet'])
    
    if returncode != 0:
        print(f"❌ FAILED: Symbol exclusion failed with code {returncode}")
        print(f"   stderr: {stderr}")
        return False
    
    password = stdout.strip()
    
    # Check that no symbols are present
    symbols = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
    has_symbols = any(char in symbols for char in password)
    
    if has_symbols:
        print(f"❌ FAILED: Password contains symbols when excluded: '{password}'")
        return False
    
    print("✅ PASSED: Symbol exclusion works")
    return True


def test_multiple_passwords():
    """Test multiple password generation."""
    print("Testing multiple password generation...")
    
    returncode, stdout, stderr = run_cli_command(['--multiple', '3', '--quiet'])
    
    if returncode != 0:
        print(f"❌ FAILED: Multiple passwords failed with code {returncode}")
        print(f"   stderr: {stderr}")
        return False
    
    passwords = stdout.strip().split('\n')
    if len(passwords) != 3:
        print(f"❌ FAILED: Expected 3 passwords, got {len(passwords)}")
        print(f"   passwords: {passwords}")
        return False
    
    # Check all passwords are different
    unique_passwords = set(passwords)
    if len(unique_passwords) != 3:
        print(f"❌ FAILED: Passwords are not unique: {passwords}")
        return False
    
    print("✅ PASSED: Multiple password generation works")
    return True


def test_config_info():
    """Test configuration information display."""
    print("Testing configuration info...")
    
    returncode, stdout, stderr = run_cli_command(['--config-info'])
    
    if returncode != 0:
        print(f"❌ FAILED: Config info failed with code {returncode}")
        print(f"   stderr: {stderr}")
        return False
    
    expected_info = [
        "Default Configuration",
        "Minimum length:",
        "Maximum length:",
        "Environment variables"
    ]
    
    for info in expected_info:
        if info not in stdout:
            print(f"❌ FAILED: Expected '{info}' in config output")
            print(f"   stdout: {stdout}")
            return False
    
    print("✅ PASSED: Config info works")
    return True


def test_rating_only():
    """Test password rating functionality."""
    print("Testing password rating...")
    
    test_password = "MyTestPassword123!"
    returncode, stdout, stderr = run_cli_command(['--rating-only', test_password])
    
    if returncode != 0:
        print(f"❌ FAILED: Rating failed with code {returncode}")
        print(f"   stderr: {stderr}")
        return False
    
    expected_content = [
        f"Password: {test_password}",
        "Length:",
        "Strength:",
        "Validation:"
    ]
    
    for content in expected_content:
        if content not in stdout:
            print(f"❌ FAILED: Expected '{content}' in rating output")
            print(f"   stdout: {stdout}")
            return False
    
    print("✅ PASSED: Password rating works")
    return True


def test_character_requirements():
    """Test character requirement options."""
    print("Testing character requirements...")
    
    # Test minimum uppercase requirement
    returncode, stdout, stderr = run_cli_command([
        '--min-upper', '3', '--length', '10', '--quiet'
    ])
    
    if returncode != 0:
        print(f"❌ FAILED: Character requirements failed with code {returncode}")
        print(f"   stderr: {stderr}")
        return False
    
    password = stdout.strip()
    uppercase_count = sum(1 for c in password if c.isupper())
    
    if uppercase_count < 3:
        print(f"❌ FAILED: Expected at least 3 uppercase chars, got {uppercase_count}")
        print(f"   password: '{password}'")
        return False
    
    print("✅ PASSED: Character requirements work")
    return True


def test_invalid_arguments():
    """Test error handling for invalid arguments."""
    print("Testing invalid argument handling...")
    
    # Test invalid length
    returncode, stdout, stderr = run_cli_command(['--length', '0'])
    
    if returncode == 0:
        print("❌ FAILED: Expected failure for zero length")
        return False
    
    if "Error:" not in stderr:
        print("❌ FAILED: Expected error message in stderr")
        print(f"   stderr: {stderr}")
        return False
    
    print("✅ PASSED: Invalid arguments handled correctly")
    return True


def main():
    """Run all CLI tests."""
    print("=== Cacao Password Generator CLI Tests ===\n")
    
    tests = [
        test_basic_generation,
        test_version,
        test_help,
        test_length_override,
        test_quiet_mode,
        test_no_symbols,
        test_multiple_passwords,
        test_config_info,
        test_rating_only,
        test_character_requirements,
        test_invalid_arguments
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Blank line after each test
        except Exception as e:
            print(f"❌ FAILED: Test {test.__name__} crashed: {e}")
            print()
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())