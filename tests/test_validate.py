"""
Comprehensive tests for cacao_password_generator.validate module.

Tests password validation functionality including basic validation,
detailed analysis, multiple password validation, and error handling.
"""

import pytest
from unittest.mock import patch, MagicMock

from cacao_password_generator.validate import (
    validate,
    validate_detailed,
    check_password_meets_minimum_requirements,
    get_validation_summary,
    validate_multiple,
    _validate_length,
    _validate_character_requirements
)
from cacao_password_generator.config import DEFAULT_CONFIG


class TestBasicValidation:
    """Test basic password validation functionality."""
    
    def test_validate_valid_password(self):
        """Test validation of a valid password."""
        password = "Test123!"  # Has upper, lower, digit, special
        is_valid, errors = validate(password)
        
        assert is_valid is True
        assert errors == []
    
    def test_validate_invalid_password_too_short(self):
        """Test validation of password that's too short."""
        password = "T1!"  # Only 3 characters, default minlen is 6
        is_valid, errors = validate(password)
        
        assert is_valid is False
        assert len(errors) == 1
        assert "too short" in errors[0]
        assert "6" in errors[0]  # Should mention minimum length
        assert "3" in errors[0]  # Should mention actual length
    
    def test_validate_invalid_password_too_long(self):
        """Test validation of password that's too long."""
        password = "Test123!" * 10  # Much longer than default maxlen of 16
        is_valid, errors = validate(password)
        
        assert is_valid is False
        assert any("too long" in error for error in errors)
    
    def test_validate_missing_uppercase(self):
        """Test validation of password missing uppercase characters."""
        password = "test123!"  # No uppercase
        is_valid, errors = validate(password)
        
        assert is_valid is False
        assert any("uppercase" in error for error in errors)
    
    def test_validate_missing_lowercase(self):
        """Test validation of password missing lowercase characters."""
        password = "TEST123!"  # No lowercase
        is_valid, errors = validate(password)
        
        assert is_valid is False
        assert any("lowercase" in error for error in errors)
    
    def test_validate_missing_digits(self):
        """Test validation of password missing digits."""
        password = "TestPass!"  # No digits
        is_valid, errors = validate(password)
        
        assert is_valid is False
        assert any("digit" in error for error in errors)
    
    def test_validate_missing_special_chars(self):
        """Test validation of password missing special characters."""
        password = "Test1234"  # No special characters
        is_valid, errors = validate(password)
        
        assert is_valid is False
        assert any("special" in error for error in errors)
    
    def test_validate_multiple_errors(self):
        """Test validation of password with multiple issues."""
        password = "test"  # Too short, no uppercase, no digits, no special
        is_valid, errors = validate(password)
        
        assert is_valid is False
        assert len(errors) >= 3  # Should have multiple errors
        assert any("too short" in error for error in errors)
        assert any("uppercase" in error for error in errors)
        assert any("digit" in error for error in errors)
        assert any("special" in error for error in errors)
    
    def test_validate_empty_password(self):
        """Test validation of empty password."""
        password = ""
        is_valid, errors = validate(password)
        
        assert is_valid is False
        assert any("empty" in error for error in errors)
    
    def test_validate_non_string_password(self):
        """Test validation handles non-string input."""
        is_valid, errors = validate(123)
        
        assert is_valid is False
        assert errors == ["Password must be a string"]
        
        is_valid, errors = validate(None)
        
        assert is_valid is False
        assert errors == ["Password must be a string"]
    
    def test_validate_with_custom_config(self):
        """Test validation with custom configuration."""
        config = {
            'minlen': 4,
            'maxlen': 8,
            'minuchars': 0,  # No uppercase required
            'minlchars': 1,
            'minnumbers': 1,
            'minschars': 0   # No special chars required
        }
        
        password = "test1"  # Should be valid with this config
        is_valid, errors = validate(password, config)
        
        assert is_valid is True
        assert errors == []


class TestLengthValidation:
    """Test length validation helper function."""
    
    def test_validate_length_valid(self):
        """Test length validation for valid password."""
        password = "Test123!"
        config = DEFAULT_CONFIG
        errors = _validate_length(password, config)
        
        assert errors == []
    
    def test_validate_length_too_short(self):
        """Test length validation for short password."""
        password = "Te1!"
        config = DEFAULT_CONFIG
        errors = _validate_length(password, config)
        
        assert len(errors) == 1
        assert "too short" in errors[0]
        assert "6" in errors[0]
        assert "4" in errors[0]
    
    def test_validate_length_too_long(self):
        """Test length validation for long password."""
        password = "Test123!" * 5  # 40 characters
        config = DEFAULT_CONFIG
        errors = _validate_length(password, config)
        
        assert len(errors) == 1
        assert "too long" in errors[0]
        assert "16" in errors[0]
        assert "40" in errors[0]
    
    def test_validate_length_both_invalid(self):
        """Test that function only reports relevant error."""
        # This shouldn't happen in practice due to config validation,
        # but testing edge case
        password = "Test123!" * 5
        config = {'minlen': 50, 'maxlen': 16}  # Invalid config
        errors = _validate_length(password, config)
        
        # Should report too long (which is the actual issue)
        assert any("too long" in error for error in errors)
    
    def test_validate_length_boundary_values(self):
        """Test length validation at boundaries."""
        config = {'minlen': 5, 'maxlen': 10}
        
        # Exactly minimum length
        errors = _validate_length("12345", config)
        assert errors == []
        
        # Exactly maximum length
        errors = _validate_length("1234567890", config)
        assert errors == []
        
        # One below minimum
        errors = _validate_length("1234", config)
        assert len(errors) == 1
        assert "too short" in errors[0]
        
        # One above maximum
        errors = _validate_length("12345678901", config)
        assert len(errors) == 1
        assert "too long" in errors[0]


class TestCharacterRequirementValidation:
    """Test character requirement validation helper function."""
    
    @patch('cacao_password_generator.validate.categorize_characters')
    @patch('cacao_password_generator.validate.get_character_requirements')
    def test_validate_character_requirements_all_met(self, mock_get_req, mock_categorize):
        """Test character validation when all requirements are met."""
        mock_categorize.return_value = {
            'uppercase': 2,
            'lowercase': 3,
            'digits': 2,
            'special': 1
        }
        mock_get_req.return_value = {
            'uppercase': 1,
            'lowercase': 1,
            'digits': 1,
            'special': 1
        }
        
        errors = _validate_character_requirements("TestPass123!", DEFAULT_CONFIG)
        assert errors == []
    
    @patch('cacao_password_generator.validate.categorize_characters')
    @patch('cacao_password_generator.validate.get_character_requirements')
    def test_validate_character_requirements_missing_uppercase(self, mock_get_req, mock_categorize):
        """Test character validation when uppercase is missing."""
        mock_categorize.return_value = {
            'uppercase': 0,
            'lowercase': 3,
            'digits': 2,
            'special': 1
        }
        mock_get_req.return_value = {
            'uppercase': 2,
            'lowercase': 1,
            'digits': 1,
            'special': 1
        }
        
        errors = _validate_character_requirements("testpass123!", DEFAULT_CONFIG)
        assert len(errors) == 1
        assert "uppercase" in errors[0]
        assert "2" in errors[0]  # Required amount
        assert "0" in errors[0]  # Actual amount
    
    @patch('cacao_password_generator.validate.categorize_characters')
    @patch('cacao_password_generator.validate.get_character_requirements')
    def test_validate_character_requirements_multiple_missing(self, mock_get_req, mock_categorize):
        """Test character validation with multiple missing requirements."""
        mock_categorize.return_value = {
            'uppercase': 0,
            'lowercase': 2,
            'digits': 0,
            'special': 0
        }
        mock_get_req.return_value = {
            'uppercase': 1,
            'lowercase': 1,
            'digits': 2,
            'special': 1
        }
        
        errors = _validate_character_requirements("testpass", DEFAULT_CONFIG)
        assert len(errors) == 3  # Missing uppercase, digits, special
        
        error_text = " ".join(errors)
        assert "uppercase" in error_text
        assert "digit" in error_text
        assert "special" in error_text


class TestDetailedValidation:
    """Test detailed validation functionality."""
    
    def test_validate_detailed_valid_password(self):
        """Test detailed validation of valid password."""
        password = "Test123!"
        result = validate_detailed(password)
        
        assert result['valid'] is True
        assert result['errors'] == []
        assert 'analysis' in result
        assert 'requirements' in result
        assert 'length_info' in result
        assert 'character_counts' in result
        
        # Check length info structure
        length_info = result['length_info']
        assert length_info['current'] == len(password)
        assert length_info['minimum'] == DEFAULT_CONFIG['minlen']
        assert length_info['maximum'] == DEFAULT_CONFIG['maxlen']
        assert length_info['valid'] is True
    
    def test_validate_detailed_invalid_password(self):
        """Test detailed validation of invalid password."""
        password = "test"  # Multiple issues
        result = validate_detailed(password)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
        
        # Check analysis structure
        analysis = result['analysis']
        for char_type in ['uppercase', 'lowercase', 'digits', 'special']:
            assert char_type in analysis
            assert 'current' in analysis[char_type]
            assert 'required' in analysis[char_type]
            assert 'valid' in analysis[char_type]
    
    def test_validate_detailed_character_analysis(self):
        """Test detailed character analysis accuracy."""
        password = "TestPass123!"
        result = validate_detailed(password)
        
        counts = result['character_counts']
        analysis = result['analysis']
        
        # Verify analysis matches character counts
        for char_type in ['uppercase', 'lowercase', 'digits', 'special']:
            assert analysis[char_type]['current'] == counts[char_type]
            assert analysis[char_type]['valid'] == (
                counts[char_type] >= analysis[char_type]['required']
            )
    
    def test_validate_detailed_with_custom_config(self):
        """Test detailed validation with custom configuration."""
        config = {
            'minlen': 8,
            'maxlen': 20,
            'minuchars': 2,
            'minlchars': 2,
            'minnumbers': 1,
            'minschars': 0
        }
        
        password = "TestPass1"
        result = validate_detailed(password, config)
        
        assert result['length_info']['minimum'] == 8
        assert result['length_info']['maximum'] == 20
        assert result['requirements']['uppercase'] == 2
        assert result['requirements']['special'] == 0


class TestQuickValidation:
    """Test quick validation functions."""
    
    def test_check_password_meets_minimum_requirements_valid(self):
        """Test quick check for valid password."""
        password = "Test123!"
        result = check_password_meets_minimum_requirements(password)
        
        assert result is True
    
    def test_check_password_meets_minimum_requirements_invalid(self):
        """Test quick check for invalid password."""
        password = "test"
        result = check_password_meets_minimum_requirements(password)
        
        assert result is False
    
    def test_check_password_meets_minimum_requirements_with_config(self):
        """Test quick check with custom configuration."""
        config = {
            'minlen': 4,
            'maxlen': 10,
            'minuchars': 0,
            'minlchars': 1,
            'minnumbers': 1,
            'minschars': 0
        }
        
        password = "test1"
        result = check_password_meets_minimum_requirements(password, config)
        
        assert result is True


class TestValidationSummary:
    """Test validation summary functionality."""
    
    def test_get_validation_summary_valid(self):
        """Test validation summary for valid password."""
        password = "Test123!"
        summary = get_validation_summary(password)
        
        assert summary == "Password meets all requirements"
    
    def test_get_validation_summary_single_error(self):
        """Test validation summary for password with single error."""
        password = "TestPass!"  # Missing digits
        summary = get_validation_summary(password)
        
        assert "1 issue:" in summary
        assert "digit" in summary.lower()
    
    def test_get_validation_summary_multiple_errors(self):
        """Test validation summary for password with multiple errors."""
        password = "test"  # Multiple issues
        summary = get_validation_summary(password)
        
        assert "issues:" in summary
        assert ";" in summary  # Should separate multiple errors
        
        # Count semicolons to verify multiple errors are listed
        error_count = summary.count(";") + 1
        assert error_count >= 2
    
    def test_get_validation_summary_with_config(self):
        """Test validation summary with custom configuration."""
        config = {
            'minlen': 10,
            'maxlen': 20,
            'minuchars': 1,
            'minlchars': 1,
            'minnumbers': 1,
            'minschars': 1
        }
        
        password = "Test123!"  # Valid normally, but too short for this config
        summary = get_validation_summary(password, config)
        
        assert "issue" in summary
        assert "short" in summary


class TestMultipleValidation:
    """Test multiple password validation functionality."""
    
    def test_validate_multiple_all_valid(self):
        """Test validation of multiple valid passwords."""
        passwords = ["Test123!", "Pass456#", "Word789$"]
        results = validate_multiple(passwords)
        
        assert len(results) == 3
        for is_valid, errors in results:
            assert is_valid is True
            assert errors == []
    
    def test_validate_multiple_mixed_validity(self):
        """Test validation of mix of valid and invalid passwords."""
        passwords = ["Test123!", "test", "Pass456#"]  # middle one invalid
        results = validate_multiple(passwords)
        
        assert len(results) == 3
        assert results[0][0] is True   # First valid
        assert results[1][0] is False  # Second invalid
        assert results[2][0] is True   # Third valid
        
        assert results[0][1] == []     # No errors for first
        assert len(results[1][1]) > 0  # Errors for second
        assert results[2][1] == []     # No errors for third
    
    def test_validate_multiple_empty_list(self):
        """Test validation of empty password list."""
        passwords = []
        results = validate_multiple(passwords)
        
        assert results == []
    
    def test_validate_multiple_with_config(self):
        """Test multiple validation with custom configuration."""
        config = {
            'minlen': 4,
            'maxlen': 8,
            'minuchars': 0,
            'minlchars': 1,
            'minnumbers': 1,
            'minschars': 0
        }
        
        passwords = ["test1", "abc", "hello2"]  # Second too short for config
        results = validate_multiple(passwords, config)
        
        assert len(results) == 3
        assert results[0][0] is True   # "test1" valid
        assert results[1][0] is False  # "abc" invalid (too short)
        assert results[2][0] is True   # "hello2" valid


class TestValidationErrorMessages:
    """Test quality and clarity of validation error messages."""
    
    def test_error_messages_include_specific_numbers(self):
        """Test that error messages include specific required and actual numbers."""
        password = "test123"  # Missing uppercase and special chars
        is_valid, errors = validate(password)
        
        assert is_valid is False
        
        # Find uppercase error
        uppercase_error = next(err for err in errors if "uppercase" in err)
        assert "1" in uppercase_error  # Required amount
        assert "0" in uppercase_error  # Actual amount
        
        # Find special character error
        special_error = next(err for err in errors if "special" in err)
        assert "1" in special_error    # Required amount
        assert "0" in special_error    # Actual amount
    
    def test_length_error_messages_clarity(self):
        """Test that length error messages are clear and specific."""
        # Too short
        password = "T1!"
        is_valid, errors = validate(password)
        length_error = next(err for err in errors if "short" in err)
        assert "6" in length_error    # Minimum length
        assert "3" in length_error    # Actual length
        
        # Too long
        password = "Test123!" * 10
        is_valid, errors = validate(password)
        length_error = next(err for err in errors if "long" in err)
        assert "16" in length_error   # Maximum length
        assert "80" in length_error   # Actual length
    
    def test_error_messages_human_readable(self):
        """Test that error messages are human-readable."""
        password = "test"
        is_valid, errors = validate(password)
        
        for error in errors:
            # Should be complete sentences
            assert error.endswith((".", ")", "s"))
            # Should be descriptive
            assert len(error.split()) >= 4
            # Should not have technical jargon
            assert "minlen" not in error
            assert "maxlen" not in error


class TestValidationIntegration:
    """Integration tests for validation functionality."""
    
    def test_validation_uses_config_system(self):
        """Test that validation properly integrates with config system."""
        # This test verifies that validate() calls load_config()
        with patch('cacao_password_generator.validate.load_config') as mock_load:
            mock_load.return_value = DEFAULT_CONFIG
            
            password = "Test123!"
            validate(password, {'minlen': 8})
            
            mock_load.assert_called_once_with({'minlen': 8})
    
    def test_validation_with_config_validation_errors(self):
        """Test validation behavior when config itself is invalid."""
        # This should be handled by the config system, but test integration
        with patch('cacao_password_generator.validate.load_config') as mock_load:
            mock_load.side_effect = ValueError("Invalid config")
            
            password = "Test123!"
            with pytest.raises(ValueError, match="Invalid config"):
                validate(password, {'invalid_key': 5})
    
    @patch('cacao_password_generator.validate.categorize_characters')
    @patch('cacao_password_generator.validate.get_character_requirements')
    def test_validation_error_handling_with_utils_failure(self, mock_get_req, mock_categorize):
        """Test validation behavior when utility functions fail."""
        mock_categorize.side_effect = Exception("Utils error")
        
        password = "Test123!"
        with pytest.raises(Exception, match="Utils error"):
            validate(password)
    
    def test_validate_detailed_consistency(self):
        """Test that validate_detailed is consistent with validate."""
        passwords = [
            "Test123!",
            "test",
            "UPPERCASE123!",
            "lowercase123!",
            "NoDigits!",
            "NoSpecial123",
            ""
        ]
        
        for password in passwords:
            basic_valid, basic_errors = validate(password)
            detailed_result = validate_detailed(password)
            
            # Basic validation should match detailed validation
            assert basic_valid == detailed_result['valid']
            assert basic_errors == detailed_result['errors']
    
    def test_all_validation_functions_consistency(self):
        """Test that all validation functions are consistent."""
        passwords = ["Test123!", "test", ""]
        
        for password in passwords:
            basic_valid, _ = validate(password)
            quick_valid = check_password_meets_minimum_requirements(password)
            detailed_valid = validate_detailed(password)['valid']
            
            # All should agree on validity
            assert basic_valid == quick_valid == detailed_valid


class TestValidationEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_validate_unicode_password(self):
        """Test validation with unicode characters."""
        password = "Tëst123!"  # Contains unicode character
        is_valid, errors = validate(password)
        
        # Should handle unicode gracefully
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)
    
    def test_validate_very_long_password(self):
        """Test validation with extremely long password."""
        password = "Test123!" * 1000  # 8000 characters
        is_valid, errors = validate(password)
        
        assert is_valid is False
        assert any("too long" in error for error in errors)
    
    def test_validate_password_with_only_special_chars(self):
        """Test password containing only special characters."""
        password = "!@#$%^&*"
        is_valid, errors = validate(password)
        
        assert is_valid is False
        # Should complain about missing uppercase, lowercase, digits
        error_text = " ".join(errors)
        assert "uppercase" in error_text
        assert "lowercase" in error_text
        assert "digit" in error_text
    
    def test_validate_boundary_character_counts(self):
        """Test validation at exact character requirement boundaries."""
        config = {
            'minlen': 8,
            'maxlen': 8,
            'minuchars': 2,
            'minlchars': 2,
            'minnumbers': 2,
            'minschars': 2
        }
        
        # Exactly meets requirements
        password = "AA11aa!!"
        is_valid, errors = validate(password, config)
        assert is_valid is True
        
        # One short on uppercase
        password = "A111aa!!"
        is_valid, errors = validate(password, config)
        assert is_valid is False
        assert any("uppercase" in error for error in errors)