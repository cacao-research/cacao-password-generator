#!/usr/bin/env python3
"""
Comprehensive test suite for cacao_password_generator.utils module.

This module tests utility functions including:
- Character set constants and definitions
- Character categorization and analysis
- Entropy calculation
- Configuration-based character set management
- Password length validation
- Character requirement extraction
"""

import pytest
import string
import math
from typing import Dict, Set, Any

from cacao_password_generator.utils import (
    UPPERCASE_CHARS,
    LOWERCASE_CHARS,
    DIGIT_CHARS,
    SPECIAL_CHARS,
    ALL_CHAR_SETS,
    ALL_CHARS,
    categorize_characters,
    get_character_space_size,
    calculate_entropy,
    get_required_chars_for_config,
    get_available_chars_for_config,
    validate_password_length,
    get_character_requirements
)


class TestCharacterConstants:
    """Test character set constants and definitions."""
    
    def test_uppercase_chars_definition(self):
        """Test uppercase character set matches expected characters."""
        expected = set(string.ascii_uppercase)
        assert UPPERCASE_CHARS == expected
        assert len(UPPERCASE_CHARS) == 26
    
    def test_lowercase_chars_definition(self):
        """Test lowercase character set matches expected characters."""
        expected = set(string.ascii_lowercase)
        assert LOWERCASE_CHARS == expected
        assert len(LOWERCASE_CHARS) == 26
    
    def test_digit_chars_definition(self):
        """Test digit character set matches expected characters."""
        expected = set(string.digits)
        assert DIGIT_CHARS == expected
        assert len(DIGIT_CHARS) == 10
    
    def test_special_chars_definition(self):
        """Test special character set contains expected symbols."""
        expected_special = "!@#$%^&*()_+-=[]{}|;:,.<>"
        assert SPECIAL_CHARS == set(expected_special)
        assert len(SPECIAL_CHARS) == len(expected_special)
    
    def test_all_char_sets_dictionary(self):
        """Test ALL_CHAR_SETS dictionary structure."""
        assert 'uppercase' in ALL_CHAR_SETS
        assert 'lowercase' in ALL_CHAR_SETS
        assert 'digits' in ALL_CHAR_SETS
        assert 'special' in ALL_CHAR_SETS
        
        assert ALL_CHAR_SETS['uppercase'] == UPPERCASE_CHARS
        assert ALL_CHAR_SETS['lowercase'] == LOWERCASE_CHARS
        assert ALL_CHAR_SETS['digits'] == DIGIT_CHARS
        assert ALL_CHAR_SETS['special'] == SPECIAL_CHARS
    
    def test_all_chars_union(self):
        """Test ALL_CHARS contains union of all character sets."""
        expected = UPPERCASE_CHARS | LOWERCASE_CHARS | DIGIT_CHARS | SPECIAL_CHARS
        assert ALL_CHARS == expected
        
        # Verify no overlap issues by checking total size
        expected_size = len(UPPERCASE_CHARS) + len(LOWERCASE_CHARS) + len(DIGIT_CHARS) + len(SPECIAL_CHARS)
        assert len(ALL_CHARS) == expected_size
    
    def test_character_sets_are_disjoint(self):
        """Test that character sets don't overlap."""
        sets = [UPPERCASE_CHARS, LOWERCASE_CHARS, DIGIT_CHARS, SPECIAL_CHARS]
        
        # Test all pairs for disjointness
        for i, set1 in enumerate(sets):
            for j, set2 in enumerate(sets):
                if i != j:
                    assert set1.isdisjoint(set2), f"Sets {i} and {j} are not disjoint"


class TestCharacterCategorization:
    """Test character categorization functionality."""
    
    def test_categorize_empty_password(self):
        """Test categorization of empty password."""
        result = categorize_characters("")
        expected = {
            'uppercase': 0,
            'lowercase': 0,
            'digits': 0,
            'special': 0,
            'other': 0
        }
        assert result == expected
    
    def test_categorize_uppercase_only(self):
        """Test categorization of uppercase-only password."""
        result = categorize_characters("ABCDEF")
        assert result['uppercase'] == 6
        assert result['lowercase'] == 0
        assert result['digits'] == 0
        assert result['special'] == 0
        assert result['other'] == 0
    
    def test_categorize_lowercase_only(self):
        """Test categorization of lowercase-only password."""
        result = categorize_characters("abcdef")
        assert result['uppercase'] == 0
        assert result['lowercase'] == 6
        assert result['digits'] == 0
        assert result['special'] == 0
        assert result['other'] == 0
    
    def test_categorize_digits_only(self):
        """Test categorization of digits-only password."""
        result = categorize_characters("123456")
        assert result['uppercase'] == 0
        assert result['lowercase'] == 0
        assert result['digits'] == 6
        assert result['special'] == 0
        assert result['other'] == 0
    
    def test_categorize_special_only(self):
        """Test categorization of special characters only."""
        result = categorize_characters("!@#$%^")
        assert result['uppercase'] == 0
        assert result['lowercase'] == 0
        assert result['digits'] == 0
        assert result['special'] == 6
        assert result['other'] == 0
    
    def test_categorize_mixed_password(self):
        """Test categorization of mixed character password."""
        result = categorize_characters("AbC123!@#")
        assert result['uppercase'] == 2  # A, C
        assert result['lowercase'] == 1  # b
        assert result['digits'] == 3     # 1, 2, 3
        assert result['special'] == 3    # !, @, #
        assert result['other'] == 0
    
    def test_categorize_unicode_characters(self):
        """Test categorization with unicode characters."""
        result = categorize_characters("Test123!éñ中")
        assert result['uppercase'] == 1  # T
        assert result['lowercase'] == 3  # e, s, t
        assert result['digits'] == 3     # 1, 2, 3
        assert result['special'] == 1    # !
        assert result['other'] == 3      # é, ñ, 中
    
    def test_categorize_repeated_characters(self):
        """Test categorization counts repeated characters correctly."""
        result = categorize_characters("AAaa11!!")
        assert result['uppercase'] == 2  # A, A
        assert result['lowercase'] == 2  # a, a
        assert result['digits'] == 2     # 1, 1
        assert result['special'] == 2    # !, !
        assert result['other'] == 0
    
    @pytest.mark.parametrize("password,expected_type,expected_count", [
        ("A", "uppercase", 1),
        ("z", "lowercase", 1),
        ("5", "digits", 1),
        ("@", "special", 1),
        ("€", "other", 1),
        ("HELLO", "uppercase", 5),
        ("world", "lowercase", 5),
        ("12345", "digits", 5),
        ("!@#$%", "special", 5),
    ])
    def test_categorize_single_types(self, password, expected_type, expected_count):
        """Test categorization for single character types."""
        result = categorize_characters(password)
        assert result[expected_type] == expected_count
        
        # Check that other types are zero
        for char_type, count in result.items():
            if char_type != expected_type:
                assert count == 0


class TestCharacterSpaceSize:
    """Test character space size calculation."""
    
    def test_empty_counts(self):
        """Test character space size for empty counts."""
        counts = {
            'uppercase': 0,
            'lowercase': 0,
            'digits': 0,
            'special': 0,
            'other': 0
        }
        assert get_character_space_size(counts) == 0
    
    def test_single_character_types(self):
        """Test character space size for single character types."""
        # Uppercase only
        counts = {'uppercase': 5, 'lowercase': 0, 'digits': 0, 'special': 0, 'other': 0}
        assert get_character_space_size(counts) == 26
        
        # Lowercase only
        counts = {'uppercase': 0, 'lowercase': 3, 'digits': 0, 'special': 0, 'other': 0}
        assert get_character_space_size(counts) == 26
        
        # Digits only
        counts = {'uppercase': 0, 'lowercase': 0, 'digits': 4, 'special': 0, 'other': 0}
        assert get_character_space_size(counts) == 10
        
        # Special only
        counts = {'uppercase': 0, 'lowercase': 0, 'digits': 0, 'special': 2, 'other': 0}
        assert get_character_space_size(counts) == len(SPECIAL_CHARS)
    
    def test_multiple_character_types(self):
        """Test character space size for multiple character types."""
        counts = {
            'uppercase': 2,
            'lowercase': 3,
            'digits': 1,
            'special': 1,
            'other': 0
        }
        expected = 26 + 26 + 10 + len(SPECIAL_CHARS)  # 26 + 26 + 10 + 25 = 87
        assert get_character_space_size(counts) == expected
    
    def test_with_other_characters(self):
        """Test character space size with 'other' characters."""
        counts = {
            'uppercase': 1,
            'lowercase': 1,
            'digits': 1,
            'special': 1,
            'other': 1
        }
        expected = 26 + 26 + 10 + len(SPECIAL_CHARS) + 10  # Add 10 for 'other'
        assert get_character_space_size(counts) == expected
    
    def test_other_characters_only(self):
        """Test character space size with only 'other' characters."""
        counts = {
            'uppercase': 0,
            'lowercase': 0,
            'digits': 0,
            'special': 0,
            'other': 3
        }
        assert get_character_space_size(counts) == 10


class TestEntropyCalculation:
    """Test password entropy calculation."""
    
    def test_empty_password_entropy(self):
        """Test entropy calculation for empty password."""
        assert calculate_entropy("") == 0.0
    
    def test_single_character_type_entropy(self):
        """Test entropy calculation for single character type passwords."""
        # Lowercase only: 4 chars from 26-char alphabet
        # Entropy = log2(26) * 4
        entropy = calculate_entropy("abcd")
        expected = math.log2(26) * 4
        assert abs(entropy - expected) < 1e-10
    
    def test_mixed_character_entropy(self):
        """Test entropy calculation for mixed character passwords."""
        # Mixed case + digits + special: "Abc1!"
        # Character space: 26 + 26 + 10 + 25 = 87
        # Length: 5
        entropy = calculate_entropy("Abc1!")
        expected = math.log2(87) * 5  # 87 = 26+26+10+25
        assert abs(entropy - expected) < 1e-10
    
    def test_all_character_types_entropy(self):
        """Test entropy with all character types present."""
        password = "Aa1!"  # One of each type
        entropy = calculate_entropy(password)
        expected_space = 26 + 26 + 10 + len(SPECIAL_CHARS)
        expected = math.log2(expected_space) * 4
        assert abs(entropy - expected) < 1e-10
    
    def test_entropy_scales_with_length(self):
        """Test that entropy scales linearly with password length."""
        base_password = "Abc1!"
        base_entropy = calculate_entropy(base_password)
        
        # Double the length
        double_password = base_password * 2
        double_entropy = calculate_entropy(double_password)
        
        # Should be exactly double (same character space, double length)
        assert abs(double_entropy - (2 * base_entropy)) < 1e-10
    
    def test_entropy_with_unicode(self):
        """Test entropy calculation with unicode characters."""
        entropy = calculate_entropy("Test é")
        # Should include space for 'other' characters (10) plus regular ones
        char_counts = categorize_characters("Test é")
        expected_space = get_character_space_size(char_counts)
        expected = math.log2(expected_space) * len("Test é")
        assert abs(entropy - expected) < 1e-10
    
    @pytest.mark.parametrize("password,expected_length", [
        ("a", 1),
        ("ab", 2),
        ("abc", 3),
        ("Test123!", 8),
        ("VeryLongPasswordWith30Characters", 32),
    ])
    def test_entropy_length_component(self, password, expected_length):
        """Test that entropy calculation uses correct password length."""
        entropy = calculate_entropy(password)
        char_counts = categorize_characters(password)
        alphabet_size = get_character_space_size(char_counts)
        
        if alphabet_size > 0:
            expected_entropy = math.log2(alphabet_size) * expected_length
            assert abs(entropy - expected_entropy) < 1e-10


class TestRequiredCharsForConfig:
    """Test required character set extraction from configuration."""
    
    def test_empty_config(self):
        """Test with empty configuration."""
        result = get_required_chars_for_config({})
        assert result == {}
    
    def test_no_requirements(self):
        """Test with zero requirements."""
        config = {
            'minuchars': 0,
            'minlchars': 0,
            'minnumbers': 0,
            'minschars': 0
        }
        result = get_required_chars_for_config(config)
        assert result == {}
    
    def test_single_requirements(self):
        """Test with single character type requirements."""
        # Uppercase only
        config = {'minuchars': 1}
        result = get_required_chars_for_config(config)
        assert result == {'uppercase': UPPERCASE_CHARS}
        
        # Lowercase only
        config = {'minlchars': 2}
        result = get_required_chars_for_config(config)
        assert result == {'lowercase': LOWERCASE_CHARS}
        
        # Digits only
        config = {'minnumbers': 1}
        result = get_required_chars_for_config(config)
        assert result == {'digits': DIGIT_CHARS}
        
        # Special only
        config = {'minschars': 3}
        result = get_required_chars_for_config(config)
        assert result == {'special': SPECIAL_CHARS}
    
    def test_multiple_requirements(self):
        """Test with multiple character type requirements."""
        config = {
            'minuchars': 2,
            'minlchars': 3,
            'minnumbers': 1,
            'minschars': 1
        }
        result = get_required_chars_for_config(config)
        expected = {
            'uppercase': UPPERCASE_CHARS,
            'lowercase': LOWERCASE_CHARS,
            'digits': DIGIT_CHARS,
            'special': SPECIAL_CHARS
        }
        assert result == expected
    
    def test_mixed_zero_and_positive_requirements(self):
        """Test with mix of zero and positive requirements."""
        config = {
            'minuchars': 1,
            'minlchars': 0,  # Should not be included
            'minnumbers': 2,
            'minschars': 0   # Should not be included
        }
        result = get_required_chars_for_config(config)
        expected = {
            'uppercase': UPPERCASE_CHARS,
            'digits': DIGIT_CHARS
        }
        assert result == expected
    
    def test_negative_values_ignored(self):
        """Test that negative values (exclusions) are ignored."""
        config = {
            'minuchars': 1,
            'minlchars': -1,  # Exclusion - should be ignored
            'minnumbers': 1,
            'minschars': -1   # Exclusion - should be ignored
        }
        result = get_required_chars_for_config(config)
        expected = {
            'uppercase': UPPERCASE_CHARS,
            'digits': DIGIT_CHARS
        }
        assert result == expected


class TestAvailableCharsForConfig:
    """Test available character set calculation from configuration."""
    
    def test_empty_config_includes_all(self):
        """Test that empty config includes all character types."""
        result = get_available_chars_for_config({})
        expected = UPPERCASE_CHARS | LOWERCASE_CHARS | DIGIT_CHARS | SPECIAL_CHARS
        assert result == expected
    
    def test_default_behavior_includes_all(self):
        """Test that default behavior includes all character types."""
        config = {}  # No explicit settings
        result = get_available_chars_for_config(config)
        assert UPPERCASE_CHARS.issubset(result)
        assert LOWERCASE_CHARS.issubset(result)
        assert DIGIT_CHARS.issubset(result)
        assert SPECIAL_CHARS.issubset(result)
    
    def test_exclude_single_character_type(self):
        """Test excluding single character types."""
        # Exclude uppercase
        config = {'minuchars': -1}
        result = get_available_chars_for_config(config)
        expected = LOWERCASE_CHARS | DIGIT_CHARS | SPECIAL_CHARS
        assert result == expected
        assert not UPPERCASE_CHARS.intersection(result)
        
        # Exclude lowercase
        config = {'minlchars': -1}
        result = get_available_chars_for_config(config)
        expected = UPPERCASE_CHARS | DIGIT_CHARS | SPECIAL_CHARS
        assert result == expected
        assert not LOWERCASE_CHARS.intersection(result)
        
        # Exclude digits
        config = {'minnumbers': -1}
        result = get_available_chars_for_config(config)
        expected = UPPERCASE_CHARS | LOWERCASE_CHARS | SPECIAL_CHARS
        assert result == expected
        assert not DIGIT_CHARS.intersection(result)
        
        # Exclude special
        config = {'minschars': -1}
        result = get_available_chars_for_config(config)
        expected = UPPERCASE_CHARS | LOWERCASE_CHARS | DIGIT_CHARS
        assert result == expected
        assert not SPECIAL_CHARS.intersection(result)
    
    def test_exclude_multiple_character_types(self):
        """Test excluding multiple character types."""
        config = {
            'minuchars': -1,  # Exclude uppercase
            'minschars': -1   # Exclude special
        }
        result = get_available_chars_for_config(config)
        expected = LOWERCASE_CHARS | DIGIT_CHARS
        assert result == expected
        assert not UPPERCASE_CHARS.intersection(result)
        assert not SPECIAL_CHARS.intersection(result)
    
    def test_positive_values_include_chars(self):
        """Test that positive values include character types."""
        config = {
            'minuchars': 1,
            'minlchars': 2,
            'minnumbers': 0,   # Zero still includes
            'minschars': 5
        }
        result = get_available_chars_for_config(config)
        expected = UPPERCASE_CHARS | LOWERCASE_CHARS | DIGIT_CHARS | SPECIAL_CHARS
        assert result == expected
    
    def test_exclude_all_falls_back_to_lowercase(self):
        """Test that excluding all types falls back to lowercase."""
        config = {
            'minuchars': -1,
            'minlchars': -1,
            'minnumbers': -1,
            'minschars': -1
        }
        result = get_available_chars_for_config(config)
        # Should fall back to lowercase to avoid empty set
        assert result == LOWERCASE_CHARS
    
    def test_mixed_inclusion_exclusion(self):
        """Test mixed inclusion and exclusion patterns."""
        config = {
            'minuchars': 2,   # Include (positive)
            'minlchars': -1,  # Exclude (negative)
            'minnumbers': 0,  # Include (zero)
            'minschars': -1   # Exclude (negative)
        }
        result = get_available_chars_for_config(config)
        expected = UPPERCASE_CHARS | DIGIT_CHARS
        assert result == expected


class TestPasswordLengthValidation:
    """Test password length validation against configuration."""
    
    def test_no_length_constraints(self):
        """Test validation with no length constraints."""
        config = {}
        assert validate_password_length("", config) is True
        assert validate_password_length("short", config) is True
        assert validate_password_length("verylongpassword", config) is True
    
    def test_minimum_length_only(self):
        """Test validation with minimum length constraint only."""
        config = {'minlen': 8}
        
        assert validate_password_length("short", config) is False  # 5 < 8
        assert validate_password_length("exactly8", config) is True  # 8 == 8
        assert validate_password_length("toolongbutok", config) is True  # 12 > 8
    
    def test_maximum_length_only(self):
        """Test validation with maximum length constraint only."""
        config = {'maxlen': 12}
        
        assert validate_password_length("short", config) is True  # 5 < 12
        assert validate_password_length("exactly12chr", config) is True  # 12 == 12
        assert validate_password_length("toolongpassword", config) is False  # 15 > 12
    
    def test_both_min_and_max_length(self):
        """Test validation with both minimum and maximum length constraints."""
        config = {'minlen': 8, 'maxlen': 16}
        
        assert validate_password_length("short", config) is False    # 5 < 8
        assert validate_password_length("exactly8", config) is True   # 8 == 8
        assert validate_password_length("mediumpass", config) is True # 10, 8 <= 10 <= 16
        assert validate_password_length("exactly16letters", config) is True  # 16 == 16
        assert validate_password_length("waytoolongpassword", config) is False  # 18 > 16
    
    def test_edge_case_lengths(self):
        """Test edge cases with length validation."""
        config = {'minlen': 1, 'maxlen': 1}
        
        assert validate_password_length("", config) is False      # 0 < 1
        assert validate_password_length("x", config) is True      # 1 == 1
        assert validate_password_length("xy", config) is False    # 2 > 1
    
    def test_empty_password_validation(self):
        """Test validation of empty password."""
        assert validate_password_length("", {}) is True
        assert validate_password_length("", {'minlen': 1}) is False
        assert validate_password_length("", {'maxlen': 0}) is True
        assert validate_password_length("", {'minlen': 0, 'maxlen': 0}) is True
    
    @pytest.mark.parametrize("password,minlen,maxlen,expected", [
        ("test", 4, 4, True),     # Exactly at both bounds
        ("test", 3, 5, True),     # Within bounds
        ("test", 5, 10, False),   # Below minimum
        ("test", 1, 3, False),    # Above maximum
        ("test", 1, 10, True),    # Within loose bounds
        ("", 0, 0, True),         # Empty password, zero bounds
        ("a", 1, 1, True),        # Single character, tight bounds
    ])
    def test_parametrized_length_validation(self, password, minlen, maxlen, expected):
        """Test various length validation scenarios."""
        config = {'minlen': minlen, 'maxlen': maxlen}
        assert validate_password_length(password, config) == expected


class TestCharacterRequirements:
    """Test character requirement extraction from configuration."""
    
    def test_empty_config(self):
        """Test character requirements with empty config."""
        result = get_character_requirements({})
        expected = {
            'uppercase': 0,
            'lowercase': 0,
            'digits': 0,
            'special': 0
        }
        assert result == expected
    
    def test_positive_requirements(self):
        """Test extraction of positive character requirements."""
        config = {
            'minuchars': 2,
            'minlchars': 3,
            'minnumbers': 1,
            'minschars': 4
        }
        result = get_character_requirements(config)
        expected = {
            'uppercase': 2,
            'lowercase': 3,
            'digits': 1,
            'special': 4
        }
        assert result == expected
    
    def test_negative_values_converted_to_zero(self):
        """Test that negative values (exclusions) are converted to zero."""
        config = {
            'minuchars': -1,  # Exclusion
            'minlchars': 2,   # Normal requirement
            'minnumbers': -1, # Exclusion
            'minschars': 0    # Zero requirement
        }
        result = get_character_requirements(config)
        expected = {
            'uppercase': 0,   # -1 converted to 0
            'lowercase': 2,   # Unchanged
            'digits': 0,      # -1 converted to 0
            'special': 0      # Unchanged
        }
        assert result == expected
    
    def test_zero_requirements(self):
        """Test extraction with all zero requirements."""
        config = {
            'minuchars': 0,
            'minlchars': 0,
            'minnumbers': 0,
            'minschars': 0
        }
        result = get_character_requirements(config)
        expected = {
            'uppercase': 0,
            'lowercase': 0,
            'digits': 0,
            'special': 0
        }
        assert result == expected
    
    def test_missing_config_keys(self):
        """Test behavior when config keys are missing."""
        config = {
            'minuchars': 1,
            # Missing: minlchars, minnumbers, minschars
        }
        result = get_character_requirements(config)
        expected = {
            'uppercase': 1,
            'lowercase': 0,  # Default when missing
            'digits': 0,     # Default when missing
            'special': 0     # Default when missing
        }
        assert result == expected
    
    def test_all_negative_values(self):
        """Test that all negative values become zero."""
        config = {
            'minuchars': -5,
            'minlchars': -10,
            'minnumbers': -1,
            'minschars': -99
        }
        result = get_character_requirements(config)
        expected = {
            'uppercase': 0,
            'lowercase': 0,
            'digits': 0,
            'special': 0
        }
        assert result == expected
    
    @pytest.mark.parametrize("config_key,expected_key", [
        ('minuchars', 'uppercase'),
        ('minlchars', 'lowercase'),
        ('minnumbers', 'digits'),
        ('minschars', 'special')
    ])
    def test_config_key_mapping(self, config_key, expected_key):
        """Test that configuration keys map correctly to requirement keys."""
        config = {config_key: 5}
        result = get_character_requirements(config)
        assert result[expected_key] == 5
        
        # Verify other keys are zero
        for key in result:
            if key != expected_key:
                assert result[key] == 0


class TestUtilityIntegration:
    """Integration tests combining multiple utility functions."""
    
    def test_categorize_and_space_size_consistency(self):
        """Test that categorization and space size calculation are consistent."""
        passwords = [
            "Test123!",
            "lowercase",
            "UPPERCASE",
            "1234567890",
            "!@#$%^&*()",
            "Mixed123!@#",
            ""
        ]
        
        for password in passwords:
            counts = categorize_characters(password)
            space_size = get_character_space_size(counts)
            
            # Space size should be zero only for empty password
            if not password:
                assert space_size == 0
            else:
                assert space_size > 0
    
    def test_entropy_and_categorization_consistency(self):
        """Test that entropy calculation is consistent with categorization."""
        password = "TestPass123!@#"
        
        # Calculate entropy directly
        entropy = calculate_entropy(password)
        
        # Calculate entropy manually using categorization
        counts = categorize_characters(password)
        space_size = get_character_space_size(counts)
        manual_entropy = math.log2(space_size) * len(password) if space_size > 0 else 0.0
        
        assert abs(entropy - manual_entropy) < 1e-10
    
    def test_config_functions_consistency(self):
        """Test consistency between config-related functions."""
        config = {
            'minuchars': 2,
            'minlchars': -1,  # Excluded
            'minnumbers': 0,
            'minschars': 1
        }
        
        # Get required and available character sets
        required = get_required_chars_for_config(config)
        available = get_available_chars_for_config(config)
        requirements = get_character_requirements(config)
        
        # Required sets should be subset of available sets
        for char_type, char_set in required.items():
            assert char_set.issubset(available)
        
        # Requirements should match required sets existence
        assert ('uppercase' in required) == (requirements['uppercase'] > 0)
        assert ('digits' in required) == (requirements['digits'] > 0)
        assert ('special' in required) == (requirements['special'] > 0)
        
        # Excluded lowercase should not be in available or required
        assert not LOWERCASE_CHARS.intersection(available)
        assert 'lowercase' not in required
        assert requirements['lowercase'] == 0