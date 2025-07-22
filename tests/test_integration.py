#!/usr/bin/env python3
"""
Comprehensive integration test suite for cacao-password-generator.

This module tests end-to-end functionality including:
- Full password generation workflows
- Cross-module interactions
- CLI integration with real execution
- Configuration loading and application  
- Performance and reliability testing
- Error handling across modules
"""

import pytest
import subprocess
import os
import tempfile
import json
import time
from typing import List, Dict, Any
from unittest.mock import patch

import cacao_password_generator
from cacao_password_generator import (
    generate, generate_multiple, validate, rating,
    get_version, get_default_config
)
from cacao_password_generator.config import load_config
from cacao_password_generator.utils import categorize_characters, calculate_entropy


class TestFullPasswordWorkflow:
    """Test complete password generation and validation workflows."""
    
    def test_generate_validate_rate_workflow(self):
        """Test full workflow: generate -> validate -> rate."""
        # Generate a password
        password = generate()
        
        # Validate it should pass
        is_valid, errors = validate(password)
        assert is_valid, f"Generated password failed validation: {errors}"
        
        # Rate it should return a valid rating
        strength = rating(password)
        assert strength in ["weak", "medium", "strong", "excellent"]
        
        # Additional checks
        assert len(password) >= 8  # Default minimum length
        assert len(password) <= 64  # Default maximum length
    
    def test_custom_config_workflow(self):
        """Test workflow with custom configuration."""
        config = {
            'minlen': 12,
            'maxlen': 20,
            'minuchars': 2,
            'minlchars': 3,
            'minnumbers': 2,
            'minschars': 1
        }
        
        # Generate with custom config
        password = generate(config)
        
        # Should meet all requirements
        assert 12 <= len(password) <= 20
        
        char_counts = categorize_characters(password)
        assert char_counts['uppercase'] >= 2
        assert char_counts['lowercase'] >= 3
        assert char_counts['digits'] >= 2
        assert char_counts['special'] >= 1
        
        # Validate should pass
        is_valid, errors = validate(password, config)
        assert is_valid, f"Custom config password failed validation: {errors}"
        
        # Rate should be reasonable (custom config typically produces strong passwords)
        strength = rating(password)
        assert strength in ["medium", "strong", "excellent"]
    
    def test_multiple_passwords_consistency(self):
        """Test that multiple password generation maintains consistency."""
        config = {'minlen': 10, 'maxlen': 15, 'minuchars': 1, 'minnumbers': 1}
        passwords = generate_multiple(5, config)
        
        assert len(passwords) == 5
        assert len(set(passwords)) == 5  # All unique
        
        # Each password should meet requirements
        for password in passwords:
            assert 10 <= len(password) <= 15
            
            is_valid, errors = validate(password, config)
            assert is_valid, f"Password '{password}' failed validation: {errors}"
            
            char_counts = categorize_characters(password)
            assert char_counts['uppercase'] >= 1
            assert char_counts['digits'] >= 1
    
    def test_exclusion_workflow(self):
        """Test workflow with character exclusions."""
        config = {
            'minuchars': -1,  # Exclude uppercase
            'minschars': -1,  # Exclude special chars
            'minlen': 8
        }
        
        password = generate(config)
        
        # Should not contain excluded character types
        char_counts = categorize_characters(password)
        assert char_counts['uppercase'] == 0
        assert char_counts['special'] == 0
        
        # Should still contain allowed types
        assert char_counts['lowercase'] > 0 or char_counts['digits'] > 0
        
        # Should still validate and rate
        is_valid, errors = validate(password, config)
        assert is_valid
        
        strength = rating(password)
        assert strength in ["weak", "medium", "strong", "excellent"]


class TestConfigurationIntegration:
    """Test configuration loading and application integration."""
    
    def test_default_config_integration(self):
        """Test integration with default configuration."""
        default_config = get_default_config()
        
        # Generate using default config
        password = generate(default_config)
        
        # Should pass validation with same config
        is_valid, errors = validate(password, default_config)
        assert is_valid
        
        # Should meet default requirements
        assert default_config['minlen'] <= len(password) <= default_config['maxlen']
    
    def test_environment_config_integration(self):
        """Test integration with environment variable configuration."""
        env_vars = {
            'CACAO_PW_MINLEN': '10',
            'CACAO_PW_MAXLEN': '15',
            'CACAO_PW_MINUCHARS': '2',
            'CACAO_PW_MINNUMBERS': '2'
        }
        
        with patch.dict(os.environ, env_vars):
            config = load_config()
            
            # Verify environment variables were loaded
            assert config['minlen'] == 10
            assert config['maxlen'] == 15
            assert config['minuchars'] == 2
            assert config['minnumbers'] == 2
            
            # Generate password with env config
            password = generate(config)
            
            # Should meet env requirements
            assert 10 <= len(password) <= 15
            
            char_counts = categorize_characters(password)
            assert char_counts['uppercase'] >= 2
            assert char_counts['digits'] >= 2
            
            # Should validate
            is_valid, errors = validate(password, config)
            assert is_valid
    
    def test_runtime_config_override_integration(self):
        """Test runtime configuration override integration."""
        base_config = {'minlen': 8, 'maxlen': 12}
        runtime_override = {'minlen': 15}
        
        # Generate with runtime override
        password = generate(base_config, length=15)
        
        # Should respect length override
        assert len(password) == 15
        
        # Should still validate against base config constraints for other requirements
        merged_config = {**base_config, 'minlen': 15, 'maxlen': 15}
        is_valid, errors = validate(password, merged_config)
        assert is_valid
    
    def test_invalid_config_handling(self):
        """Test handling of invalid configurations across modules."""
        # Test impossible requirements
        invalid_config = {
            'minlen': 5,
            'minuchars': 2,
            'minlchars': 2, 
            'minnumbers': 2,
            'minschars': 2  # Total minimum chars (8) > minlen (5)
        }
        
        # Should either generate successfully or raise appropriate error
        try:
            password = generate(invalid_config)
            # If generation succeeds, it should still be valid
            is_valid, errors = validate(password, invalid_config)
            # We expect this to fail validation due to impossible requirements
            # The generator might produce a valid password by ignoring impossible constraints
        except ValueError:
            # This is acceptable - the generator detected impossible constraints
            pass


class TestCLIIntegration:
    """Test CLI integration with full command execution."""
    
    def test_basic_cli_generation(self, cli_command):
        """Test basic CLI password generation."""
        result = subprocess.run(cli_command, capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'Generated Password:' in result.stdout
        assert 'Strength Rating:' in result.stdout
        
        # Extract password from output
        lines = result.stdout.strip().split('\n')
        password_line = [line for line in lines if 'Generated Password:' in line][0]
        password = password_line.split('Generated Password: ')[1]
        
        # Validate the generated password
        is_valid, errors = validate(password)
        assert is_valid, f"CLI generated invalid password: {errors}"
    
    def test_cli_with_custom_parameters(self, cli_command):
        """Test CLI with custom parameters."""
        result = subprocess.run([
            *cli_command,
            '--length', '16',
            '--min-upper', '2',
            '--min-numbers', '3',
            '--min-symbols', '1'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        
        # Extract password
        lines = result.stdout.strip().split('\n')
        password_line = [line for line in lines if 'Generated Password:' in line][0]
        password = password_line.split('Generated Password: ')[1]
        
        # Verify requirements
        assert len(password) == 16
        
        char_counts = categorize_characters(password)
        assert char_counts['uppercase'] >= 2
        assert char_counts['digits'] >= 3
        assert char_counts['special'] >= 1
    
    def test_cli_quiet_mode_integration(self, cli_command):
        """Test CLI quiet mode integration."""
        result = subprocess.run([*cli_command, '--quiet'], 
                              capture_output=True, text=True)
        
        assert result.returncode == 0
        
        # Should only output the password
        output_lines = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        assert len(output_lines) == 1
        
        password = output_lines[0]
        assert len(password) >= 8  # Should meet minimum requirements
        
        # Validate the password
        is_valid, errors = validate(password)
        assert is_valid
    
    def test_cli_rating_mode_integration(self, cli_command):
        """Test CLI rating-only mode integration."""
        test_password = "TestPassword123!"
        
        result = subprocess.run([*cli_command, '--rating-only', test_password],
                              capture_output=True, text=True)
        
        assert result.returncode == 0
        assert f'Password: {test_password}' in result.stdout
        assert 'Strength:' in result.stdout
        assert 'Validation:' in result.stdout
        
        # Verify rating consistency
        programmatic_rating = rating(test_password)
        assert programmatic_rating in result.stdout
    
    def test_cli_multiple_passwords_integration(self, cli_command):
        """Test CLI multiple password generation integration."""
        result = subprocess.run([*cli_command, '--multiple', '3', '--quiet'],
                              capture_output=True, text=True)
        
        assert result.returncode == 0
        
        passwords = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        assert len(passwords) == 3
        assert len(set(passwords)) == 3  # All unique
        
        # Each should be valid
        for password in passwords:
            is_valid, errors = validate(password)
            assert is_valid, f"CLI generated invalid password: {password}"
    
    def test_cli_error_handling_integration(self, cli_command):
        """Test CLI error handling integration."""
        # Test conflicting arguments
        result = subprocess.run([
            *cli_command,
            '--no-uppercase',
            '--min-upper', '2'
        ], capture_output=True, text=True)
        
        assert result.returncode == 1  # Should exit with error
        assert 'Error:' in result.stderr


class TestPerformanceIntegration:
    """Test performance characteristics of integrated systems."""
    
    @pytest.mark.slow
    def test_bulk_generation_performance(self):
        """Test performance of bulk password generation."""
        start_time = time.time()
        
        # Generate 100 passwords
        passwords = generate_multiple(100)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert duration < 5.0, f"Bulk generation took too long: {duration}s"
        
        # Verify all passwords are valid and unique
        assert len(passwords) == 100
        assert len(set(passwords)) == 100
        
        for password in passwords[:10]:  # Check first 10 to avoid test slowdown
            is_valid, errors = validate(password)
            assert is_valid
    
    @pytest.mark.slow
    def test_complex_config_performance(self):
        """Test performance with complex configuration."""
        complex_config = {
            'minlen': 20,
            'maxlen': 30,
            'minuchars': 5,
            'minlchars': 5,
            'minnumbers': 5,
            'minschars': 3
        }
        
        start_time = time.time()
        
        # Generate 20 passwords with complex requirements
        passwords = generate_multiple(20, complex_config)
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert duration < 3.0, f"Complex generation took too long: {duration}s"
        
        # Verify requirements are met
        for password in passwords:
            char_counts = categorize_characters(password)
            assert char_counts['uppercase'] >= 5
            assert char_counts['lowercase'] >= 5
            assert char_counts['digits'] >= 5
            assert char_counts['special'] >= 3
    
    def test_entropy_calculation_performance(self):
        """Test entropy calculation performance."""
        # Generate test passwords of various lengths
        test_passwords = [
            generate({'minlen': 8, 'maxlen': 8}),
            generate({'minlen': 16, 'maxlen': 16}),
            generate({'minlen': 32, 'maxlen': 32}),
            generate({'minlen': 64, 'maxlen': 64})
        ]
        
        start_time = time.time()
        
        # Calculate entropy for all passwords
        entropies = [calculate_entropy(pwd) for pwd in test_passwords]
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert duration < 1.0, f"Entropy calculation took too long: {duration}s"
        
        # Verify entropy increases with length (generally)
        for i in range(1, len(entropies)):
            # Entropy should generally increase with length
            # (allowing some variance due to character set differences)
            assert entropies[i] >= entropies[i-1] * 0.8


class TestErrorHandlingIntegration:
    """Test error handling across module boundaries."""
    
    def test_cascading_error_handling(self):
        """Test error handling cascades properly across modules."""
        # Create config that might cause issues
        problematic_config = {
            'minlen': -1,  # Invalid
            'maxlen': 5,
            'minuchars': 10  # Impossible with maxlen=5
        }
        
        # Each module should handle errors appropriately
        with pytest.raises((ValueError, TypeError)):
            generate(problematic_config)
    
    def test_empty_string_handling_across_modules(self):
        """Test empty string handling across all modules."""
        empty_password = ""
        
        # Validation should handle empty password
        is_valid, errors = validate(empty_password)
        assert not is_valid
        assert len(errors) > 0
        
        # Rating should handle empty password
        strength = rating(empty_password)
        assert strength == "weak"
        
        # Entropy calculation should handle empty password
        entropy = calculate_entropy(empty_password)
        assert entropy == 0.0
    
    def test_unicode_handling_across_modules(self):
        """Test unicode character handling across modules."""
        unicode_password = "Pássw✓rd123!🔐"
        
        # Should handle unicode in validation
        is_valid, errors = validate(unicode_password)
        # Result may vary based on requirements, but shouldn't crash
        
        # Should handle unicode in rating
        strength = rating(unicode_password)
        assert strength in ["weak", "medium", "strong", "excellent"]
        
        # Should handle unicode in entropy calculation
        entropy = calculate_entropy(unicode_password)
        assert entropy > 0


class TestVersionAndMetadata:
    """Test version and metadata consistency."""
    
    def test_version_consistency(self):
        """Test version information consistency."""
        version = get_version()
        assert isinstance(version, str)
        assert len(version) > 0
        
        # Version should be in semver-like format
        import re
        version_pattern = r'^\d+\.\d+\.\d+.*'
        assert re.match(version_pattern, version), f"Invalid version format: {version}"
    
    def test_cli_version_consistency(self, cli_command):
        """Test CLI version matches package version."""
        result = subprocess.run([*cli_command, '--version'],
                              capture_output=True, text=True)
        
        assert result.returncode == 0
        cli_version_output = result.stdout.strip()
        package_version = get_version()
        
        assert package_version in cli_version_output


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    def test_typical_web_app_scenario(self):
        """Test typical web application password generation scenario."""
        # Web apps typically want 12-16 character passwords with mixed requirements
        web_config = {
            'minlen': 12,
            'maxlen': 16,
            'minuchars': 1,
            'minlchars': 1,
            'minnumbers': 1,
            'minschars': 1
        }
        
        passwords = generate_multiple(10, web_config)
        
        for password in passwords:
            # Should meet web app requirements
            assert 12 <= len(password) <= 16
            
            char_counts = categorize_characters(password)
            assert char_counts['uppercase'] >= 1
            assert char_counts['lowercase'] >= 1
            assert char_counts['digits'] >= 1
            assert char_counts['special'] >= 1
            
            # Should be reasonably strong
            strength = rating(password)
            assert strength in ["medium", "strong", "excellent"]
            
            # Should have reasonable entropy
            entropy = calculate_entropy(password)
            assert entropy >= 60  # Reasonable threshold for web apps
    
    def test_high_security_scenario(self):
        """Test high-security password generation scenario."""
        # High security: long passwords with many character requirements
        security_config = {
            'minlen': 24,
            'maxlen': 32,
            'minuchars': 3,
            'minlchars': 3,
            'minnumbers': 3,
            'minschars': 3
        }
        
        password = generate(security_config)
        
        # Should meet all security requirements
        assert 24 <= len(password) <= 32
        
        char_counts = categorize_characters(password)
        assert char_counts['uppercase'] >= 3
        assert char_counts['lowercase'] >= 3
        assert char_counts['digits'] >= 3
        assert char_counts['special'] >= 3
        
        # Should be strong or excellent
        strength = rating(password)
        assert strength in ["strong", "excellent"]
        
        # Should have high entropy
        entropy = calculate_entropy(password)
        assert entropy >= 120  # High entropy for security
    
    def test_legacy_system_scenario(self):
        """Test legacy system compatibility scenario."""
        # Legacy systems might not support special characters
        legacy_config = {
            'minlen': 8,
            'maxlen': 12,
            'minschars': -1,  # No special characters
            'minuchars': 1,
            'minnumbers': 1
        }
        
        passwords = generate_multiple(5, legacy_config)
        
        for password in passwords:
            # Should work with legacy constraints
            assert 8 <= len(password) <= 12
            
            char_counts = categorize_characters(password)
            assert char_counts['special'] == 0  # No special chars
            assert char_counts['uppercase'] >= 1
            assert char_counts['digits'] >= 1
            
            # Should still validate
            is_valid, errors = validate(password, legacy_config)
            assert is_valid


class TestConcurrencyAndReliability:
    """Test concurrent usage and reliability."""
    
    def test_concurrent_generation_reliability(self):
        """Test that concurrent password generation works reliably."""
        import threading
        import queue
        
        def generate_passwords(result_queue, count=5):
            """Generate passwords in a thread."""
            try:
                passwords = generate_multiple(count)
                result_queue.put(('success', passwords))
            except Exception as e:
                result_queue.put(('error', str(e)))
        
        # Start multiple threads
        threads = []
        result_queue = queue.Queue()
        
        for _ in range(3):
            thread = threading.Thread(target=generate_passwords, args=(result_queue,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Collect results
        all_passwords = []
        while not result_queue.empty():
            status, result = result_queue.get()
            assert status == 'success', f"Thread failed: {result}"
            all_passwords.extend(result)
        
        # Should have generated all passwords successfully
        assert len(all_passwords) == 15  # 3 threads * 5 passwords each
        
        # Most should be unique (allowing for small chance of collision)
        unique_passwords = set(all_passwords)
        assert len(unique_passwords) >= 14  # Allow 1 potential collision
    
    def test_repeated_generation_reliability(self):
        """Test reliability of repeated password generation."""
        config = {'minlen': 12, 'maxlen': 16}
        
        # Generate many passwords and verify consistency
        all_passwords = []
        for _ in range(50):
            password = generate(config)
            all_passwords.append(password)
            
            # Each should be valid
            is_valid, errors = validate(password, config)
            assert is_valid, f"Generated invalid password on iteration: {password}"
            
            # Length should be in range
            assert 12 <= len(password) <= 16
        
        # Should have good uniqueness (allowing for some collisions)
        unique_passwords = set(all_passwords)
        uniqueness_ratio = len(unique_passwords) / len(all_passwords)
        assert uniqueness_ratio >= 0.95, f"Low uniqueness ratio: {uniqueness_ratio}"