#!/usr/bin/env python3
"""
Comprehensive tests for enhanced detailed_rating() functionality.

Tests the enhanced detailed_rating() function that returns comprehensive JSON structure
with crack time analysis, password score, character set analysis, and suggestions.
"""

import pytest
import json
import math
from unittest.mock import patch, MagicMock

from cacao_password_generator.rating import (
    detailed_rating,
    calculate_crack_time,
    format_crack_time,
    calculate_password_score
)


class TestEnhancedDetailedRating:
    """Test the enhanced detailed_rating() function structure and completeness."""
    
    def test_detailed_rating_complete_structure(self):
        """Test that detailed_rating returns the complete expected structure."""
        result = detailed_rating("TestPassword123!")
        
        # Check all required top-level keys are present
        expected_keys = {
            'rating', 'entropy', 'diversity_score', 'pattern_penalty',
            'crack_time_seconds', 'crack_time_formatted', 'password_score',
            'character_set_size', 'character_analysis', 'length_analysis',
            'suggestions'
        }
        
        assert set(result.keys()) == expected_keys
    
    def test_detailed_rating_data_types(self):
        """Test that all fields have correct data types."""
        result = detailed_rating("TestPassword123!")
        
        # Basic metrics
        assert isinstance(result['rating'], str)
        assert isinstance(result['entropy'], (int, float))
        assert isinstance(result['diversity_score'], (int, float))
        assert isinstance(result['pattern_penalty'], (int, float))
        assert isinstance(result['crack_time_seconds'], (int, float))
        assert isinstance(result['crack_time_formatted'], str)
        assert isinstance(result['password_score'], int)
        assert isinstance(result['character_set_size'], int)
        
        # Nested structures
        assert isinstance(result['character_analysis'], dict)
        assert isinstance(result['length_analysis'], dict)
        assert isinstance(result['suggestions'], list)
    
    def test_character_analysis_structure(self):
        """Test character_analysis nested structure."""
        result = detailed_rating("TestPassword123!")
        char_analysis = result['character_analysis']
        
        # Check required keys
        expected_keys = {'character_counts', 'types_present', 'diversity_level'}
        assert set(char_analysis.keys()) == expected_keys
        
        # Check character_counts structure
        char_counts = char_analysis['character_counts']
        expected_count_keys = {'uppercase', 'lowercase', 'digits', 'special'}
        assert set(char_counts.keys()) == expected_count_keys
        
        # Check all counts are non-negative integers
        for count in char_counts.values():
            assert isinstance(count, int)
            assert count >= 0
        
        # Check types_present is integer
        assert isinstance(char_analysis['types_present'], int)
        assert 0 <= char_analysis['types_present'] <= 4
        
        # Check diversity_level is valid
        assert char_analysis['diversity_level'] in ['minimal', 'basic', 'good', 'excellent']
    
    def test_length_analysis_structure(self):
        """Test length_analysis nested structure."""
        result = detailed_rating("TestPassword123!")
        length_analysis = result['length_analysis']
        
        # Check required keys
        expected_keys = {'length', 'length_bonus', 'length_penalty'}
        assert set(length_analysis.keys()) == expected_keys
        
        # Check data types
        assert isinstance(length_analysis['length'], int)
        assert isinstance(length_analysis['length_bonus'], (int, float))
        assert isinstance(length_analysis['length_penalty'], (int, float))
        
        # Check length is positive
        assert length_analysis['length'] > 0
        
        # Check bonus/penalty are reasonable values
        assert 0.5 <= length_analysis['length_bonus'] <= 2.0
        assert 0.5 <= length_analysis['length_penalty'] <= 2.0
    
    def test_suggestions_structure(self):
        """Test suggestions list structure."""
        result = detailed_rating("TestPassword123!")
        suggestions = result['suggestions']
        
        # Should be a list of strings
        assert isinstance(suggestions, list)
        assert all(isinstance(suggestion, str) for suggestion in suggestions)
        assert len(suggestions) > 0  # Should always have at least one suggestion
    
    def test_detailed_rating_empty_password(self):
        """Test detailed rating structure for empty password."""
        result = detailed_rating("")
        
        # Should have all required keys even for empty password
        expected_keys = {
            'rating', 'entropy', 'diversity_score', 'pattern_penalty',
            'crack_time_seconds', 'crack_time_formatted', 'password_score',
            'character_set_size', 'character_analysis', 'length_analysis',
            'suggestions'
        }
        assert set(result.keys()) == expected_keys
        
        # Check specific empty password values
        assert result['rating'] == 'weak'
        assert result['entropy'] == 0.0
        assert result['diversity_score'] == 0.0
        assert result['pattern_penalty'] == 0.0
        assert result['crack_time_seconds'] == 0.0
        assert result['crack_time_formatted'] == 'less than 1 second'
        assert result['password_score'] == 0
        assert result['character_set_size'] == 0
        assert result['suggestions'] == ['Password is empty or invalid']
        
        # Check empty character analysis
        char_analysis = result['character_analysis']
        assert char_analysis['types_present'] == 0
        assert char_analysis['diversity_level'] == 'minimal'
        assert all(count == 0 for count in char_analysis['character_counts'].values())
        
        # Check empty length analysis
        length_analysis = result['length_analysis']
        assert length_analysis['length'] == 0
        assert length_analysis['length_bonus'] == 1.0
        assert length_analysis['length_penalty'] == 1.0
    
    def test_detailed_rating_invalid_input(self):
        """Test detailed rating with invalid input types."""
        for invalid_input in [None, 123, [], {}, object()]:
            result = detailed_rating(invalid_input)
            
            # Should handle gracefully and return weak rating structure
            assert result['rating'] == 'weak'
            assert result['entropy'] == 0.0
            assert result['suggestions'] == ['Password is empty or invalid']


class TestDetailedRatingEdgeCases:
    """Test edge cases for detailed rating functionality."""
    
    def test_very_short_password(self):
        """Test detailed rating for very short password."""
        result = detailed_rating("A")
        
        assert result['rating'] == 'weak'
        assert result['length_analysis']['length'] == 1
        assert result['length_analysis']['length_penalty'] == 0.7  # Should get penalty
        assert result['character_analysis']['types_present'] == 1
        assert result['character_analysis']['diversity_level'] == 'minimal'
        
        # Should have length-related suggestions
        suggestion_text = ' '.join(result['suggestions'])
        assert 'length' in suggestion_text.lower() or '8 characters' in suggestion_text
    
    def test_very_long_password(self):
        """Test detailed rating for very long password."""
        long_password = "A" * 100 + "b" * 20 + "1" * 10 + "!" * 5  # 135 chars
        result = detailed_rating(long_password)
        
        assert result['length_analysis']['length'] == 135
        assert result['length_analysis']['length_bonus'] == 1.1  # Should get bonus
        assert result['character_analysis']['types_present'] == 4
        assert result['character_analysis']['diversity_level'] == 'excellent'
        
        # Should be high entropy and score
        assert result['entropy'] > 100
        assert result['password_score'] > 50
    
    def test_all_character_types_password(self):
        """Test password with all character types."""
        password = "Abc123!@#"
        result = detailed_rating(password)
        
        char_analysis = result['character_analysis']
        char_counts = char_analysis['character_counts']
        
        # Should have all character types
        assert char_counts['uppercase'] > 0
        assert char_counts['lowercase'] > 0
        assert char_counts['digits'] > 0
        assert char_counts['special'] > 0
        assert char_analysis['types_present'] == 4
        assert char_analysis['diversity_level'] == 'excellent'
    
    def test_single_character_type_password(self):
        """Test password with only one character type."""
        password = "abcdefgh"
        result = detailed_rating(password)
        
        char_analysis = result['character_analysis']
        char_counts = char_analysis['character_counts']
        
        # Should have only lowercase
        assert char_counts['uppercase'] == 0
        assert char_counts['lowercase'] > 0
        assert char_counts['digits'] == 0
        assert char_counts['special'] == 0
        assert char_analysis['types_present'] == 1
        assert char_analysis['diversity_level'] == 'minimal'
    
    def test_password_with_patterns(self):
        """Test password with detectable patterns."""
        password = "password123abc"
        result = detailed_rating(password)
        
        # Should have pattern penalty
        assert result['pattern_penalty'] > 0
        
        # Should have pattern-related suggestions
        suggestion_text = ' '.join(result['suggestions'])
        assert 'pattern' in suggestion_text.lower() or 'dictionary' in suggestion_text.lower()
    
    def test_password_with_repetition(self):
        """Test password with character repetition."""
        password = "Test111!"
        result = detailed_rating(password)
        
        # Should have pattern penalty for repetition
        assert result['pattern_penalty'] > 0
    
    def test_unicode_password(self):
        """Test password with unicode characters."""
        password = "Tëst123!@#"
        result = detailed_rating(password)
        
        # Should handle unicode gracefully
        assert isinstance(result['rating'], str)
        assert result['entropy'] > 0
        assert result['character_set_size'] > 0


class TestCrackTimeCalculations:
    """Test crack time calculation components."""
    
    def test_crack_time_calculation(self):
        """Test crack time calculation accuracy."""
        password = "Test123!"
        result = detailed_rating(password)
        
        # Crack time should be positive
        assert result['crack_time_seconds'] > 0
        assert isinstance(result['crack_time_formatted'], str)
        assert len(result['crack_time_formatted']) > 0
    
    def test_crack_time_scaling(self):
        """Test that longer passwords have longer crack times."""
        short_password = "Te1!"
        long_password = "TestPassword123!@#$%"
        
        short_result = detailed_rating(short_password)
        long_result = detailed_rating(long_password)
        
        # Long password should take much longer to crack
        assert long_result['crack_time_seconds'] > short_result['crack_time_seconds']
        assert long_result['password_score'] > short_result['password_score']
    
    def test_password_score_range(self):
        """Test password score is in valid range."""
        passwords = ["a", "Test123!", "VeryStrongPassword123!@#$%^&*()"]
        
        for password in passwords:
            result = detailed_rating(password)
            score = result['password_score']
            
            # Score should be in 0-100 range
            assert 0 <= score <= 100
            assert isinstance(score, int)
    
    def test_crack_time_formatting(self):
        """Test crack time formatting for various durations."""
        # Test with known values
        assert format_crack_time(0.5) == "less than 1 second"
        assert format_crack_time(1.0) == "1 second"
        assert format_crack_time(60.0) == "1 minute"
        assert format_crack_time(3600.0) == "1 hour"
        assert format_crack_time(86400.0) == "1 day"
        
        # Test larger values contain expected units
        large_time_str = format_crack_time(365.25 * 24 * 3600)  # 1 year
        assert "year" in large_time_str
    
    def test_password_score_calculation(self):
        """Test password score calculation."""
        # Test boundary cases
        assert calculate_password_score(0) == 0
        assert calculate_password_score(-1) == 0
        
        # Test reasonable values
        score_1000 = calculate_password_score(1000)  # ~10^3 seconds
        score_million = calculate_password_score(1_000_000)  # ~10^6 seconds
        
        assert 0 <= score_1000 <= 100
        assert 0 <= score_million <= 100
        assert score_million > score_1000  # Longer time should have higher score


class TestSuggestionGeneration:
    """Test password improvement suggestion generation."""
    
    def test_suggestions_for_weak_password(self):
        """Test suggestions for weak password."""
        result = detailed_rating("test")
        suggestions = result['suggestions']
        
        suggestion_text = ' '.join(suggestions)
        
        # Should suggest various improvements
        assert any(keyword in suggestion_text.lower() for keyword in [
            'length', 'uppercase', 'numbers', 'special', 'characters'
        ])
    
    def test_suggestions_for_good_password(self):
        """Test suggestions for already good password."""
        result = detailed_rating("TestPasswordWithAllTypes123!@#")
        suggestions = result['suggestions']
        
        # Should indicate password is good
        assert any('good' in suggestion.lower() for suggestion in suggestions)
    
    def test_suggestions_specificity(self):
        """Test that suggestions are specific to missing elements."""
        # Password missing uppercase
        result = detailed_rating("test123!")
        suggestions = ' '.join(result['suggestions'])
        assert 'uppercase' in suggestions.lower()
        
        # Password missing special characters
        result = detailed_rating("Test123")
        suggestions = ' '.join(result['suggestions'])
        assert 'special' in suggestions.lower()
        
        # Password missing digits
        result = detailed_rating("TestPass!")
        suggestions = ' '.join(result['suggestions'])
        assert 'numbers' in suggestions.lower() or 'digits' in suggestions.lower()
    
    def test_suggestions_for_common_patterns(self):
        """Test suggestions detect common patterns."""
        result = detailed_rating("password123")
        suggestions = ' '.join(result['suggestions'])
        
        # Should detect dictionary word
        assert any(keyword in suggestions.lower() for keyword in [
            'dictionary', 'common', 'pattern'
        ])


class TestDetailedRatingIntegration:
    """Test integration of detailed_rating with other components."""
    
    def test_detailed_rating_consistency(self):
        """Test that detailed rating is consistent with basic rating."""
        from cacao_password_generator.rating import rating
        
        passwords = [
            "weak",
            "Test123!",
            "VeryStrongPassword123!@#$%",
            "ExtremelyLongAndComplexPasswordWithAllTypes123!@#$%^&*()"
        ]
        
        for password in passwords:
            basic_rating = rating(password)
            detailed_result = detailed_rating(password)
            
            # Basic rating should match detailed rating
            assert basic_rating == detailed_result['rating']
    
    def test_detailed_rating_serializable(self):
        """Test that detailed rating result is JSON serializable."""
        result = detailed_rating("TestPassword123!")
        
        # Should be able to serialize to JSON without errors
        json_str = json.dumps(result)
        assert len(json_str) > 0
        
        # Should be able to deserialize back
        deserialized = json.loads(json_str)
        assert deserialized == result
    
    def test_detailed_rating_performance(self):
        """Test that detailed rating performs reasonably."""
        import time
        
        # Test with various password lengths
        passwords = [
            "Test123!",
            "MediumLengthPassword123!",
            "VeryLongPasswordWithManyCharactersIncludingAllTypes123!@#$%^&*()"
        ]
        
        for password in passwords:
            start_time = time.time()
            result = detailed_rating(password)
            end_time = time.time()
            
            # Should complete in reasonable time (less than 1 second)
            assert end_time - start_time < 1.0
            assert isinstance(result, dict)  # Should return valid result


class TestDetailedRatingRealWorldExamples:
    """Test detailed rating with real-world password examples."""
    
    @pytest.mark.parametrize("password,expected_rating", [
        ("123456", "weak"),
        ("password", "weak"),
        ("Password123", "medium"),
        ("MySecureP@ssw0rd!", "strong"),
        ("Tr0ub4dor&3", "strong"),
        ("correct horse battery staple", "medium"),  # Long but predictable
        ("X7#mK9$pQ2@vL5&nR8*jT4%wE6!uI3^yO1", "excellent"),  # Random strong
    ])
    def test_real_world_passwords(self, password, expected_rating):
        """Test detailed rating on real-world password examples."""
        result = detailed_rating(password)
        
        # Check that rating matches expectation (allowing some flexibility)
        ratings_hierarchy = {"weak": 0, "medium": 1, "strong": 2, "excellent": 3}
        actual_level = ratings_hierarchy[result['rating']]
        expected_level = ratings_hierarchy[expected_rating]
        
        # Allow +/- 1 level difference for edge cases
        assert abs(actual_level - expected_level) <= 1
        
        # Ensure all fields are present
        assert all(key in result for key in [
            'rating', 'entropy', 'crack_time_formatted', 'suggestions'
        ])