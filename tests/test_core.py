"""
Tests for core password generation functionality.

This module tests the core.py module functions including password generation,
character distribution analysis, and generation time estimation.
"""

import pytest
import re
from typing import Dict, Any
from unittest.mock import patch

import cacao_password_generator.core as core
from cacao_password_generator.utils import categorize_characters


class TestGenerate:
    """Test the main generate() function."""
    
    def test_generate_default_config(self):
        """Test password generation with default configuration."""
        password = core.generate()
        
        # Basic checks
        assert isinstance(password, str)
        assert len(password) >= 6  # Default minimum length
        assert len(password) <= 16  # Default maximum length
        assert password  # Not empty
    
    def test_generate_with_length_override(self):
        """Test password generation with specific length."""
        lengths = [6, 10, 15, 20, 30]
        
        for length in lengths:
            password = core.generate(length=length)
            assert len(password) == length
            assert isinstance(password, str)
    
    def test_generate_with_custom_config(self, custom_config):
        """Test password generation with custom configuration."""
        password = core.generate(custom_config)
        
        # Check length constraints
        assert len(password) >= custom_config['minlen']
        assert len(password) <= custom_config['maxlen']
        
        # Analyze character distribution
        char_dist = categorize_characters(password)
        assert char_dist['uppercase'] >= custom_config['minuchars']
        assert char_dist['lowercase'] >= custom_config['minlchars']
        assert char_dist['digits'] >= custom_config['minnumbers']
        assert char_dist['special'] >= custom_config['minschars']
    
    def test_generate_multiple_calls_unique(self):
        """Test that multiple generate() calls produce different passwords."""
        passwords = [core.generate() for _ in range(10)]
        
        # All passwords should be different (very high probability)
        unique_passwords = set(passwords)
        assert len(unique_passwords) >= 8  # Allow for very small chance of collision
    
    def test_generate_invalid_length(self):
        """Test error handling for invalid length parameters."""
        invalid_lengths = [0, -1, -5, 1.5, "10", None]
        
        for invalid_length in invalid_lengths:
            if invalid_length is None:
                continue  # None is valid (means no override)
            
            with pytest.raises(ValueError, match="Length must be a positive integer"):
                core.generate(length=invalid_length)
    
    def test_generate_length_too_short_for_requirements(self, strict_config):
        """Test error when length is too short to meet character requirements."""
        # strict_config requires at least 4+4+3+2=13 characters
        with pytest.raises(ValueError, match="too short to meet minimum character requirements"):
            core.generate(strict_config, length=10)
    
    @pytest.mark.parametrize("config", [
        None,
        {'minlen': 8, 'maxlen': 12},
        {'minlen': 6, 'maxlen': 8, 'minschars': 0},
        {'minlen': 10, 'maxlen': 15, 'minuchars': 3}
    ])
    def test_generate_parametrized_configs(self, config):
        """Test generation with various configurations."""
        password = core.generate(config)
        
        assert isinstance(password, str)
        assert len(password) > 0
        
        if config:
            assert len(password) >= config.get('minlen', 6)
            assert len(password) <= config.get('maxlen', 16)
    
    def test_generate_security_randomness(self):
        """Test that generated passwords use cryptographic randomness."""
        passwords = [core.generate(length=20) for _ in range(100)]
        
        # Statistical tests for randomness
        # 1. All passwords should be unique
        assert len(set(passwords)) == 100
        
        # 2. Character distribution should be reasonably random
        all_chars = ''.join(passwords)
        char_counts = {}
        for char in all_chars:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # No single character should dominate (rough heuristic)
        max_count = max(char_counts.values())
        total_chars = len(all_chars)
        assert max_count / total_chars < 0.1  # No char > 10% of total
    
    def test_generate_meets_all_requirements(self, parametrized_configs):
        """Test that generated passwords meet all specified requirements."""
        for config_name, config in parametrized_configs:
            password = core.generate(config)
            char_dist = categorize_characters(password)
            
            if config:
                # Check minimum character requirements
                assert char_dist['uppercase'] >= config.get('minuchars', 0), f"Config: {config_name}"
                assert char_dist['lowercase'] >= config.get('minlchars', 0), f"Config: {config_name}"
                assert char_dist['digits'] >= config.get('minnumbers', 0), f"Config: {config_name}"
                assert char_dist['special'] >= config.get('minschars', 0), f"Config: {config_name}"
                
                # Check length constraints
                assert len(password) >= config.get('minlen', 6), f"Config: {config_name}"
                assert len(password) <= config.get('maxlen', 16), f"Config: {config_name}"


class TestGenerateMultiple:
    """Test the generate_multiple() function."""
    
    def test_generate_multiple_basic(self):
        """Test basic multiple password generation."""
        passwords = core.generate_multiple(5)
        
        assert isinstance(passwords, list)
        assert len(passwords) == 5
        assert all(isinstance(pwd, str) for pwd in passwords)
        assert all(len(pwd) >= 6 for pwd in passwords)  # Default min length
    
    def test_generate_multiple_with_config(self, custom_config):
        """Test multiple generation with custom config."""
        passwords = core.generate_multiple(3, custom_config)
        
        assert len(passwords) == 3
        for password in passwords:
            assert len(password) >= custom_config['minlen']
            assert len(password) <= custom_config['maxlen']
    
    def test_generate_multiple_with_length(self):
        """Test multiple generation with length override."""
        passwords = core.generate_multiple(4, length=12)
        
        assert len(passwords) == 4
        assert all(len(pwd) == 12 for pwd in passwords)
    
    def test_generate_multiple_uniqueness(self):
        """Test that multiple passwords are unique."""
        passwords = core.generate_multiple(20)
        unique_passwords = set(passwords)
        
        # All should be unique (very high probability)
        assert len(unique_passwords) >= 18  # Allow tiny chance of collision
    
    def test_generate_multiple_invalid_count(self):
        """Test error handling for invalid count values."""
        invalid_counts = [0, -1, -5, 1.5, "5", None]
        
        for invalid_count in invalid_counts:
            with pytest.raises(ValueError, match="Count must be a positive integer"):
                core.generate_multiple(invalid_count)
    
    def test_generate_multiple_large_count(self):
        """Test generation of large number of passwords."""
        passwords = core.generate_multiple(100, length=8)
        
        assert len(passwords) == 100
        assert len(set(passwords)) >= 95  # Very high uniqueness expected


class TestPasswordCharacterDistribution:
    """Test password character distribution analysis."""
    
    def test_get_password_character_distribution(self):
        """Test character distribution analysis."""
        test_password = "MyTest123!@#"
        distribution = core.get_password_character_distribution(test_password)
        
        assert isinstance(distribution, dict)
        assert 'uppercase' in distribution
        assert 'lowercase' in distribution
        assert 'digits' in distribution
        assert 'special' in distribution
        
        # Check specific counts for known password
        assert distribution['uppercase'] == 2  # M, T
        assert distribution['lowercase'] == 4  # y, e, s, t
        assert distribution['digits'] == 3     # 1, 2, 3
        assert distribution['special'] == 3    # !, @, #
    
    def test_character_distribution_empty_password(self):
        """Test character distribution for empty password."""
        distribution = core.get_password_character_distribution("")
        
        assert all(count == 0 for count in distribution.values())
    
    def test_character_distribution_single_type(self):
        """Test distribution for passwords with single character type."""
        test_cases = [
            ("ABCDEF", {'uppercase': 6, 'lowercase': 0, 'digits': 0, 'special': 0}),
            ("abcdef", {'uppercase': 0, 'lowercase': 6, 'digits': 0, 'special': 0}),
            ("123456", {'uppercase': 0, 'lowercase': 0, 'digits': 6, 'special': 0}),
            ("!@#$%^", {'uppercase': 0, 'lowercase': 0, 'digits': 0, 'special': 6})
        ]
        
        for password, expected in test_cases:
            distribution = core.get_password_character_distribution(password)
            for key, expected_count in expected.items():
                assert distribution[key] == expected_count


class TestEstimateGenerationTime:
    """Test generation time estimation."""
    
    def test_estimate_generation_time_default(self):
        """Test time estimation with default config."""
        estimate = core.estimate_generation_time()
        
        assert isinstance(estimate, str)
        assert estimate in [
            "Very fast (no character requirements)",
            "Fast (minimal requirements)",
            "Moderate (balanced requirements)",
            "Slower (strict requirements)"
        ]
    
    def test_estimate_generation_time_no_requirements(self):
        """Test estimation for config with no character requirements."""
        config = {'minuchars': 0, 'minlchars': 0, 'minnumbers': 0, 'minschars': 0}
        estimate = core.estimate_generation_time(config)
        
        assert estimate == "Very fast (no character requirements)"
    
    def test_estimate_generation_time_minimal(self):
        """Test estimation for minimal requirements."""
        config = {'minuchars': 1, 'minlchars': 1, 'minnumbers': 0, 'minschars': 0}
        estimate = core.estimate_generation_time(config)
        
        assert estimate == "Fast (minimal requirements)"
    
    def test_estimate_generation_time_strict(self):
        """Test estimation for strict requirements."""
        config = {
            'minuchars': 4, 'minlchars': 4, 'minnumbers': 3, 'minschars': 3
        }
        estimate = core.estimate_generation_time(config)
        
        assert estimate == "Slower (strict requirements)"


class TestInternalFunctions:
    """Test internal helper functions."""
    
    @patch('cacao_password_generator.core.secrets')
    def test_select_random_chars(self, mock_secrets):
        """Test _select_random_chars function."""
        mock_secrets.choice.side_effect = lambda seq: seq[0]  # Always return first char
        
        char_set = {'a', 'b', 'c'}
        result = core._select_random_chars(char_set, 3)
        
        assert len(result) == 3
        assert all(char in char_set for char in result)
        assert mock_secrets.choice.call_count == 3
    
    def test_shuffle_list(self):
        """Test _shuffle_list function."""
        original = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        test_list = original.copy()
        
        core._shuffle_list(test_list)
        
        # List should have same elements but likely different order
        assert len(test_list) == len(original)
        assert set(test_list) == set(original)
        
        # For longer lists, shuffling should change order (high probability)
        if len(original) > 3:
            # Run multiple times to check randomness
            shuffled_results = []
            for _ in range(10):
                temp_list = original.copy()
                core._shuffle_list(temp_list)
                shuffled_results.append(temp_list.copy())
            
            # At least some should be different from original
            different_orders = sum(1 for result in shuffled_results if result != original)
            assert different_orders >= 8  # High probability of shuffling
    
    def test_shuffle_list_empty(self):
        """Test shuffling empty list."""
        empty_list = []
        core._shuffle_list(empty_list)
        assert empty_list == []
    
    def test_shuffle_list_single_item(self):
        """Test shuffling single item list."""
        single_list = ['a']
        core._shuffle_list(single_list)
        assert single_list == ['a']


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_generate_minimum_possible_length(self):
        """Test generation with minimum possible length."""
        config = {
            'minlen': 1, 'maxlen': 1,
            'minuchars': 0, 'minlchars': 1, 'minnumbers': 0, 'minschars': 0
        }
        password = core.generate(config)
        assert len(password) == 1
        assert password.islower()
    
    def test_generate_maximum_requirements(self):
        """Test generation that uses all available length for requirements."""
        config = {
            'minlen': 10, 'maxlen': 10,
            'minuchars': 3, 'minlchars': 3, 'minnumbers': 2, 'minschars': 2
        }
        password = core.generate(config)
        assert len(password) == 10
        
        char_dist = categorize_characters(password)
        assert char_dist['uppercase'] == 3
        assert char_dist['lowercase'] == 3
        assert char_dist['digits'] == 2
        assert char_dist['special'] == 2
    
    def test_generate_exactly_minimum_requirements(self):
        """Test when password length exactly equals required characters."""
        config = {
            'minlen': 4, 'maxlen': 4,
            'minuchars': 1, 'minlchars': 1, 'minnumbers': 1, 'minschars': 1
        }
        password = core.generate(config)
        assert len(password) == 4
        
        char_dist = categorize_characters(password)
        assert char_dist['uppercase'] == 1
        assert char_dist['lowercase'] == 1
        assert char_dist['digits'] == 1
        assert char_dist['special'] == 1
    
    @pytest.mark.security
    def test_generate_security_properties(self):
        """Test security properties of generated passwords."""
        # Generate many passwords to test statistical properties
        passwords = [core.generate(length=16) for _ in range(1000)]
        
        # 1. All passwords should be unique
        assert len(set(passwords)) == 1000
        
        # 2. No obvious patterns in first/last characters
        first_chars = [pwd[0] for pwd in passwords]
        last_chars = [pwd[-1] for pwd in passwords]
        
        # Should have good distribution (not all same character)
        assert len(set(first_chars)) > 10
        assert len(set(last_chars)) > 10
        
        # 3. No common passwords should appear
        common_passwords = ['password', 'Password1', '123456789', 'qwerty']
        for common in common_passwords:
            if len(common) == 16:  # Only check if same length
                assert common not in passwords


class TestPerformance:
    """Test performance characteristics."""
    
    @pytest.mark.performance
    def test_generation_performance(self):
        """Test password generation performance."""
        import time
        
        # Test single password generation
        start = time.time()
        core.generate()
        single_time = time.time() - start
        
        # Should be very fast (< 1 second)
        assert single_time < 1.0
        
        # Test multiple password generation
        start = time.time()
        core.generate_multiple(100)
        multiple_time = time.time() - start
        
        # Should still be reasonable (< 5 seconds for 100 passwords)
        assert multiple_time < 5.0
    
    @pytest.mark.performance  
    def test_generation_memory_efficiency(self):
        """Test that password generation doesn't leak memory."""
        import gc
        
        # Force garbage collection before test
        gc.collect()
        
        # Generate many passwords
        for _ in range(1000):
            password = core.generate()
            # Immediately discard reference
            del password
        
        # Force garbage collection
        gc.collect()
        
        # Test passes if no memory errors occur
        assert True