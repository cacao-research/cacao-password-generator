"""
Comprehensive tests for cacao_password_generator.rating module.

Tests password strength rating functionality including entropy-based rating,
detailed analysis, pattern detection, and comparative analysis.
"""

import pytest
from unittest.mock import patch, MagicMock

from cacao_password_generator.rating import (
    rating,
    detailed_rating,
    rate_multiple,
    compare_passwords,
    _calculate_diversity_score,
    _calculate_pattern_penalty,
    _is_sequential,
    _get_diversity_level,
    _generate_suggestions,
    ENTROPY_THRESHOLDS,
    DIVERSITY_THRESHOLDS
)


class TestConstants:
    """Test rating module constants."""
    
    def test_entropy_thresholds(self):
        """Test entropy threshold constants."""
        expected_thresholds = {
            'weak': 0,
            'medium': 30,
            'strong': 50,
            'excellent': 70
        }
        assert ENTROPY_THRESHOLDS == expected_thresholds
    
    def test_diversity_thresholds(self):
        """Test diversity threshold constants."""
        expected_thresholds = {
            'minimal': 1,
            'basic': 2,
            'good': 3,
            'excellent': 4
        }
        assert DIVERSITY_THRESHOLDS == expected_thresholds


class TestBasicRating:
    """Test basic password rating functionality."""
    
    @patch('cacao_password_generator.rating.calculate_entropy')
    @patch('cacao_password_generator.rating.categorize_characters')
    def test_rating_excellent_password(self, mock_categorize, mock_entropy):
        """Test rating of excellent password."""
        mock_entropy.return_value = 80.0  # High entropy
        mock_categorize.return_value = {
            'uppercase': 3,
            'lowercase': 5,
            'digits': 2,
            'special': 2
        }
        
        result = rating("TestPass123!@#")
        assert result == "excellent"
    
    @patch('cacao_password_generator.rating.calculate_entropy')
    @patch('cacao_password_generator.rating.categorize_characters')
    def test_rating_strong_password(self, mock_categorize, mock_entropy):
        """Test rating of strong password."""
        mock_entropy.return_value = 55.0  # Strong entropy
        mock_categorize.return_value = {
            'uppercase': 2,
            'lowercase': 4,
            'digits': 2,
            'special': 1
        }
        
        result = rating("TestPass123!")
        assert result == "strong"
    
    @patch('cacao_password_generator.rating.calculate_entropy')
    @patch('cacao_password_generator.rating.categorize_characters')
    def test_rating_medium_password(self, mock_categorize, mock_entropy):
        """Test rating of medium strength password."""
        mock_entropy.return_value = 35.0  # Medium entropy
        mock_categorize.return_value = {
            'uppercase': 1,
            'lowercase': 4,
            'digits': 1,
            'special': 0
        }
        
        result = rating("Test123")
        assert result == "medium"
    
    @patch('cacao_password_generator.rating.calculate_entropy')
    @patch('cacao_password_generator.rating.categorize_characters')
    def test_rating_weak_password(self, mock_categorize, mock_entropy):
        """Test rating of weak password."""
        mock_entropy.return_value = 15.0  # Low entropy
        mock_categorize.return_value = {
            'uppercase': 0,
            'lowercase': 4,
            'digits': 0,
            'special': 0
        }
        
        result = rating("test")
        assert result == "weak"
    
    def test_rating_empty_password(self):
        """Test rating of empty password."""
        result = rating("")
        assert result == "weak"
    
    def test_rating_non_string_input(self):
        """Test rating handles non-string input."""
        assert rating(123) == "weak"
        assert rating(None) == "weak"
        assert rating([]) == "weak"
    
    @patch('cacao_password_generator.rating.calculate_entropy')
    @patch('cacao_password_generator.rating.categorize_characters')
    def test_rating_length_penalty(self, mock_categorize, mock_entropy):
        """Test that short passwords get penalized."""
        mock_entropy.return_value = 40.0
        mock_categorize.return_value = {
            'uppercase': 1,
            'lowercase': 2,
            'digits': 1,
            'special': 1
        }
        
        # Short password should get penalized (40 * 0.7 = 28, which is weak)
        result = rating("T3st!")  # 5 characters
        assert result == "weak"
    
    @patch('cacao_password_generator.rating.calculate_entropy')
    @patch('cacao_password_generator.rating.categorize_characters')
    def test_rating_length_bonus(self, mock_categorize, mock_entropy):
        """Test that long passwords get bonuses."""
        mock_entropy.return_value = 45.0  # Just below strong threshold
        mock_categorize.return_value = {
            'uppercase': 2,
            'lowercase': 8,
            'digits': 2,
            'special': 2
        }
        
        # Long password should get bonus (45 * 1.1 = 49.5, still medium)
        # But close to strong threshold
        result = rating("TestPassword123!")  # 16 characters
        # Should be medium, but close to strong due to bonus
        assert result in ["medium", "strong"]


class TestDiversityScoring:
    """Test character diversity scoring functionality."""
    
    def test_calculate_diversity_score_all_types(self):
        """Test diversity score with all character types."""
        char_counts = {
            'uppercase': 2,
            'lowercase': 3,
            'digits': 2,
            'special': 1
        }
        score = _calculate_diversity_score(char_counts)
        assert score == 10.0  # Excellent diversity
    
    def test_calculate_diversity_score_three_types(self):
        """Test diversity score with three character types."""
        char_counts = {
            'uppercase': 2,
            'lowercase': 3,
            'digits': 2,
            'special': 0
        }
        score = _calculate_diversity_score(char_counts)
        assert score == 6.0  # Good diversity
    
    def test_calculate_diversity_score_two_types(self):
        """Test diversity score with two character types."""
        char_counts = {
            'uppercase': 2,
            'lowercase': 3,
            'digits': 0,
            'special': 0
        }
        score = _calculate_diversity_score(char_counts)
        assert score == 3.0  # Basic diversity
    
    def test_calculate_diversity_score_one_type(self):
        """Test diversity score with only one character type."""
        char_counts = {
            'uppercase': 0,
            'lowercase': 5,
            'digits': 0,
            'special': 0
        }
        score = _calculate_diversity_score(char_counts)
        assert score == 0.0  # Minimal diversity
    
    def test_calculate_diversity_score_no_characters(self):
        """Test diversity score with no characters."""
        char_counts = {
            'uppercase': 0,
            'lowercase': 0,
            'digits': 0,
            'special': 0
        }
        score = _calculate_diversity_score(char_counts)
        assert score == 0.0


class TestPatternPenalty:
    """Test pattern penalty calculation functionality."""
    
    def test_calculate_pattern_penalty_no_patterns(self):
        """Test penalty calculation for password with no patterns."""
        penalty = _calculate_pattern_penalty("Tr7$kL9@")
        assert penalty == 0.0
    
    def test_calculate_pattern_penalty_sequential_chars(self):
        """Test penalty for sequential characters."""
        penalty = _calculate_pattern_penalty("abc123def")
        assert penalty > 0  # Should have penalty for "abc" and "123"
    
    def test_calculate_pattern_penalty_repeated_chars(self):
        """Test penalty for repeated characters."""
        penalty = _calculate_pattern_penalty("password111")
        assert penalty >= 3.0  # Should have penalty for "111"
    
    def test_calculate_pattern_penalty_common_patterns(self):
        """Test penalty for common patterns."""
        penalty = _calculate_pattern_penalty("password123")
        assert penalty >= 5.0  # Should have penalty for "password"
        
        penalty = _calculate_pattern_penalty("admin456")
        assert penalty >= 5.0  # Should have penalty for "admin"
    
    def test_calculate_pattern_penalty_multiple_issues(self):
        """Test penalty accumulation for multiple pattern issues."""
        penalty = _calculate_pattern_penalty("passwordaaa123")
        # Should have penalties for: "password" pattern, "aaa" repetition, "123" sequence
        assert penalty >= 10.0
    
    def test_calculate_pattern_penalty_case_insensitive(self):
        """Test that pattern detection is case insensitive."""
        penalty1 = _calculate_pattern_penalty("PASSWORD")
        penalty2 = _calculate_pattern_penalty("password")
        assert penalty1 == penalty2


class TestSequentialDetection:
    """Test sequential character detection."""
    
    def test_is_sequential_ascending_letters(self):
        """Test detection of ascending letter sequences."""
        assert _is_sequential("abc") is True
        assert _is_sequential("def") is True
        assert _is_sequential("xyz") is True
    
    def test_is_sequential_descending_letters(self):
        """Test detection of descending letter sequences."""
        assert _is_sequential("cba") is True
        assert _is_sequential("fed") is True
        assert _is_sequential("zyx") is True
    
    def test_is_sequential_ascending_numbers(self):
        """Test detection of ascending number sequences."""
        assert _is_sequential("123") is True
        assert _is_sequential("456") is True
        assert _is_sequential("789") is True
    
    def test_is_sequential_descending_numbers(self):
        """Test detection of descending number sequences."""
        assert _is_sequential("321") is True
        assert _is_sequential("654") is True
        assert _is_sequential("987") is True
    
    def test_is_sequential_non_sequential(self):
        """Test that non-sequential patterns are not detected."""
        assert _is_sequential("acb") is False
        assert _is_sequential("135") is False
        assert _is_sequential("aaa") is False
        assert _is_sequential("a1b") is False
    
    def test_is_sequential_wrong_length(self):
        """Test that sequences of wrong length are not detected."""
        assert _is_sequential("ab") is False
        assert _is_sequential("abcd") is False
        assert _is_sequential("") is False


class TestDiversityLevel:
    """Test diversity level categorization."""
    
    def test_get_diversity_level_excellent(self):
        """Test excellent diversity level."""
        assert _get_diversity_level(4) == "excellent"
        assert _get_diversity_level(5) == "excellent"  # Edge case
    
    def test_get_diversity_level_good(self):
        """Test good diversity level."""
        assert _get_diversity_level(3) == "good"
    
    def test_get_diversity_level_basic(self):
        """Test basic diversity level."""
        assert _get_diversity_level(2) == "basic"
    
    def test_get_diversity_level_minimal(self):
        """Test minimal diversity level."""
        assert _get_diversity_level(1) == "minimal"
        assert _get_diversity_level(0) == "minimal"


class TestDetailedRating:
    """Test detailed password rating analysis."""
    
    @patch('cacao_password_generator.rating.calculate_entropy')
    @patch('cacao_password_generator.rating.categorize_characters')
    def test_detailed_rating_structure(self, mock_categorize, mock_entropy):
        """Test that detailed rating returns expected structure."""
        mock_entropy.return_value = 45.0
        mock_categorize.return_value = {
            'uppercase': 1,
            'lowercase': 4,
            'digits': 2,
            'special': 1
        }
        
        result = detailed_rating("Test123!")
        
        # Check all expected keys are present
        expected_keys = [
            'rating', 'entropy', 'diversity_score', 'pattern_penalty',
            'character_analysis', 'length_analysis', 'suggestions'
        ]
        for key in expected_keys:
            assert key in result
        
        # Check data types
        assert isinstance(result['rating'], str)
        assert isinstance(result['entropy'], float)
        assert isinstance(result['diversity_score'], float)
        assert isinstance(result['pattern_penalty'], float)
        assert isinstance(result['character_analysis'], dict)
        assert isinstance(result['length_analysis'], dict)
        assert isinstance(result['suggestions'], list)
    
    def test_detailed_rating_empty_password(self):
        """Test detailed rating of empty password."""
        result = detailed_rating("")
        
        assert result['rating'] == 'weak'
        assert result['entropy'] == 0.0
        assert result['diversity_score'] == 0.0
        assert result['pattern_penalty'] == 0.0
        assert result['suggestions'] == ['Password is empty or invalid']
    
    def test_detailed_rating_non_string(self):
        """Test detailed rating of non-string input."""
        result = detailed_rating(123)
        
        assert result['rating'] == 'weak'
        assert result['entropy'] == 0.0
        assert result['suggestions'] == ['Password is empty or invalid']
    
    @patch('cacao_password_generator.rating.calculate_entropy')
    @patch('cacao_password_generator.rating.categorize_characters')
    def test_detailed_rating_length_analysis(self, mock_categorize, mock_entropy):
        """Test length analysis in detailed rating."""
        mock_entropy.return_value = 30.0
        mock_categorize.return_value = {
            'uppercase': 1, 'lowercase': 10, 'digits': 3, 'special': 2
        }
        
        # Test long password (16+ characters)
        result = detailed_rating("TestPassword123!")  # 16 chars
        length_analysis = result['length_analysis']
        
        assert length_analysis['length'] == 16
        assert length_analysis['length_bonus'] == 1.1
        assert length_analysis['length_penalty'] == 1.0
        
        # Test short password (<6 characters)
        result = detailed_rating("T3st!")  # 5 chars
        length_analysis = result['length_analysis']
        
        assert length_analysis['length'] == 5
        assert length_analysis['length_bonus'] == 1.0
        assert length_analysis['length_penalty'] == 0.7
    
    @patch('cacao_password_generator.rating.categorize_characters')
    def test_detailed_rating_character_analysis(self, mock_categorize):
        """Test character analysis in detailed rating."""
        mock_categorize.return_value = {
            'uppercase': 2,
            'lowercase': 4,
            'digits': 1,
            'special': 1
        }
        
        result = detailed_rating("TestPass1!")
        char_analysis = result['character_analysis']
        
        assert 'character_counts' in char_analysis
        assert 'types_present' in char_analysis
        assert 'diversity_level' in char_analysis
        
        assert char_analysis['types_present'] == 4
        assert char_analysis['diversity_level'] == "excellent"
    
    def test_detailed_rating_integration(self):
        """Test that detailed rating integrates properly with main rating."""
        password = "TestPassword123!"
        basic_rating = rating(password)
        detailed_result = detailed_rating(password)
        
        assert basic_rating == detailed_result['rating']


class TestSuggestionGeneration:
    """Test password improvement suggestion generation."""
    
    def test_generate_suggestions_short_password(self):
        """Test suggestions for short password."""
        char_counts = {'uppercase': 1, 'lowercase': 3, 'digits': 1, 'special': 0}
        suggestions = _generate_suggestions("Test1", char_counts, 3)
        
        suggestion_text = " ".join(suggestions)
        assert "length" in suggestion_text.lower()
        assert "8 characters" in suggestion_text
    
    def test_generate_suggestions_missing_character_types(self):
        """Test suggestions for missing character types."""
        char_counts = {'uppercase': 0, 'lowercase': 4, 'digits': 0, 'special': 0}
        suggestions = _generate_suggestions("test", char_counts, 1)
        
        suggestion_text = " ".join(suggestions)
        assert "uppercase" in suggestion_text.lower()
        assert "numbers" in suggestion_text.lower()
        assert "special" in suggestion_text.lower()
    
    def test_generate_suggestions_common_patterns(self):
        """Test suggestions for common patterns."""
        char_counts = {'uppercase': 0, 'lowercase': 8, 'digits': 0, 'special': 0}
        suggestions = _generate_suggestions("password", char_counts, 1)
        
        suggestion_text = " ".join(suggestions)
        assert "common" in suggestion_text.lower() or "dictionary" in suggestion_text.lower()
    
    def test_generate_suggestions_good_password(self):
        """Test suggestions for already good password."""
        char_counts = {'uppercase': 2, 'lowercase': 6, 'digits': 2, 'special': 2}
        suggestions = _generate_suggestions("TestPassword123!", char_counts, 4)
        
        assert "Password strength is good!" in suggestions
    
    def test_generate_suggestions_medium_length(self):
        """Test suggestions for medium length password."""
        char_counts = {'uppercase': 2, 'lowercase': 6, 'digits': 2, 'special': 1}
        suggestions = _generate_suggestions("TestPass12!", char_counts, 4)  # 11 chars
        
        suggestion_text = " ".join(suggestions)
        assert "12+" in suggestion_text


class TestMultipleRating:
    """Test multiple password rating functionality."""
    
    def test_rate_multiple_basic(self):
        """Test rating multiple passwords."""
        passwords = ["Test123!", "weakpass", "ExcellentPassword123!@#"]
        results = rate_multiple(passwords)
        
        assert len(results) == 3
        assert all(isinstance(rating, str) for rating in results)
        assert all(rating in ["weak", "medium", "strong", "excellent"] 
                  for rating in results)
    
    def test_rate_multiple_empty_list(self):
        """Test rating empty password list."""
        results = rate_multiple([])
        assert results == []
    
    def test_rate_multiple_mixed_inputs(self):
        """Test rating multiple passwords with mixed valid/invalid inputs."""
        passwords = ["Test123!", "", None, "Good4Pass!"]
        results = rate_multiple(passwords)
        
        assert len(results) == 4
        # Empty and None should both be rated as weak
        assert results[1] == "weak"  # Empty string
        assert results[2] == "weak"  # None


class TestPasswordComparison:
    """Test password comparison functionality."""
    
    @patch('cacao_password_generator.rating.calculate_entropy')
    def test_compare_passwords_first_stronger(self, mock_entropy):
        """Test comparison where first password is stronger."""
        mock_entropy.side_effect = [60.0, 40.0]  # First password has higher entropy
        
        with patch('cacao_password_generator.rating.rating') as mock_rating:
            mock_rating.side_effect = ["strong", "medium"]
            
            result = compare_passwords("StrongPass123!", "weakpass")
            
            assert result['password1_rating'] == "strong"
            assert result['password2_rating'] == "medium"
            assert result['stronger'] == "password1"
            assert result['entropy_difference'] == 20.0
    
    @patch('cacao_password_generator.rating.calculate_entropy')
    def test_compare_passwords_second_stronger(self, mock_entropy):
        """Test comparison where second password is stronger."""
        mock_entropy.side_effect = [30.0, 70.0]
        
        with patch('cacao_password_generator.rating.rating') as mock_rating:
            mock_rating.side_effect = ["medium", "excellent"]
            
            result = compare_passwords("mediumpass", "ExcellentPass123!@#")
            
            assert result['stronger'] == "password2"
            assert result['entropy_difference'] == 40.0
    
    @patch('cacao_password_generator.rating.calculate_entropy')
    def test_compare_passwords_tie(self, mock_entropy):
        """Test comparison where passwords have equal strength."""
        mock_entropy.side_effect = [50.0, 52.0]  # Similar entropy
        
        with patch('cacao_password_generator.rating.rating') as mock_rating:
            mock_rating.side_effect = ["strong", "strong"]
            
            result = compare_passwords("StrongPass1!", "StrongPass2#")
            
            assert result['stronger'] == "tie"
            assert result['entropy_difference'] == 2.0
    
    def test_compare_passwords_structure(self):
        """Test that comparison returns expected structure."""
        result = compare_passwords("Test123!", "Pass456#")
        
        expected_keys = [
            'password1_rating', 'password2_rating', 
            'password1_entropy', 'password2_entropy',
            'stronger', 'entropy_difference'
        ]
        
        for key in expected_keys:
            assert key in result
        
        assert isinstance(result['entropy_difference'], float)
        assert result['stronger'] in ["password1", "password2", "tie"]


class TestRatingIntegration:
    """Integration tests for rating functionality."""
    
    def test_rating_uses_utility_functions(self):
        """Test that rating integrates with utility functions."""
        with patch('cacao_password_generator.rating.calculate_entropy') as mock_entropy:
            with patch('cacao_password_generator.rating.categorize_characters') as mock_categorize:
                mock_entropy.return_value = 45.0
                mock_categorize.return_value = {
                    'uppercase': 1, 'lowercase': 4, 'digits': 2, 'special': 1
                }
                
                rating("Test123!")
                
                mock_entropy.assert_called_once_with("Test123!")
                mock_categorize.assert_called_once_with("Test123!")
    
    def test_rating_consistency_across_functions(self):
        """Test that all rating functions are consistent."""
        password = "TestPassword123!"
        
        basic_rating = rating(password)
        detailed_result = detailed_rating(password)
        multiple_result = rate_multiple([password])[0]
        
        # All should agree on the rating
        assert basic_rating == detailed_result['rating']
        assert basic_rating == multiple_result
    
    def test_rating_handles_utility_failures(self):
        """Test rating behavior when utility functions fail."""
        with patch('cacao_password_generator.rating.calculate_entropy') as mock_entropy:
            mock_entropy.side_effect = Exception("Entropy calculation failed")
            
            # Should handle gracefully or propagate exception
            with pytest.raises(Exception):
                rating("Test123!")


class TestRatingEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_rating_boundary_entropy_values(self):
        """Test rating at entropy boundaries."""
        test_cases = [
            (29.9, "weak"),     # Just below medium threshold
            (30.0, "medium"),   # Exactly at medium threshold  
            (49.9, "medium"),   # Just below strong threshold
            (50.0, "strong"),   # Exactly at strong threshold
            (69.9, "strong"),   # Just below excellent threshold
            (70.0, "excellent") # Exactly at excellent threshold
        ]
        
        for entropy_value, expected_rating in test_cases:
            with patch('cacao_password_generator.rating.calculate_entropy') as mock_entropy:
                with patch('cacao_password_generator.rating.categorize_characters') as mock_categorize:
                    mock_entropy.return_value = entropy_value
                    mock_categorize.return_value = {
                        'uppercase': 1, 'lowercase': 4, 'digits': 2, 'special': 1
                    }
                    
                    result = rating("Test123!")
                    assert result == expected_rating
    
    def test_rating_very_long_password(self):
        """Test rating of extremely long password."""
        long_password = "TestPassword123!" * 100  # 1600 characters
        result = rating(long_password)
        
        assert isinstance(result, str)
        assert result in ["weak", "medium", "strong", "excellent"]
    
    def test_rating_unicode_characters(self):
        """Test rating with unicode characters."""
        unicode_password = "Tëst123!@#Ñ"
        result = rating(unicode_password)
        
        assert isinstance(result, str)
        assert result in ["weak", "medium", "strong", "excellent"]
    
    def test_rating_special_character_edge_cases(self):
        """Test rating with various special characters."""
        special_passwords = [
            "Test123!@#$%^&*()",
            "Test123!<>?{}[]|\\",
            "Test123!`~-_=+",
            "Test123!\"':;,."
        ]
        
        for password in special_passwords:
            result = rating(password)
            assert isinstance(result, str)
            assert result in ["weak", "medium", "strong", "excellent"]
    
    def test_pattern_penalty_edge_cases(self):
        """Test pattern penalty calculation edge cases."""
        edge_cases = [
            "",  # Empty string
            "a",  # Single character
            "ab",  # Two characters
            "aaaaaaaaaaaaaaa",  # All same character
            "abcdefghijklmno",  # Long sequence
            "012345678901234"   # Numeric sequence
        ]
        
        for password in edge_cases:
            penalty = _calculate_pattern_penalty(password)
            assert isinstance(penalty, float)
            assert penalty >= 0.0


class TestRatingPerformance:
    """Test rating performance characteristics."""
    
    @pytest.mark.slow
    def test_rating_large_batch(self):
        """Test rating performance with large batch of passwords."""
        passwords = [f"TestPass{i}!" for i in range(1000)]
        
        results = rate_multiple(passwords)
        
        assert len(results) == 1000
        assert all(isinstance(rating, str) for rating in results)
    
    def test_detailed_rating_performance(self):
        """Test that detailed rating completes in reasonable time."""
        password = "TestPassword123!@#ComplexPassword"
        
        result = detailed_rating(password)
        
        # Should complete and return valid structure
        assert isinstance(result, dict)
        assert 'rating' in result
        assert 'suggestions' in result