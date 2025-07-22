"""
Comprehensive tests for cacao_password_generator.config module.

Tests configuration management including defaults, environment variables,
runtime overrides, validation, and error handling.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from cacao_password_generator.config import (
    load_config,
    get_default_config,
    get_config_from_env,
    _validate_config,
    DEFAULT_CONFIG,
    ENV_PREFIX,
    VALID_CONFIG_KEYS
)


class TestDefaultConfig:
    """Test default configuration values and constants."""
    
    def test_default_config_values(self):
        """Test that default config has expected structure and values."""
        expected = {
            'minlen': 6,
            'maxlen': 16,
            'minuchars': 1,
            'minlchars': 1,
            'minnumbers': 1,
            'minschars': 1,
        }
        assert DEFAULT_CONFIG == expected
    
    def test_default_config_is_dict(self):
        """Test that default config is a dictionary."""
        assert isinstance(DEFAULT_CONFIG, dict)
        assert len(DEFAULT_CONFIG) == 6
    
    def test_valid_config_keys(self):
        """Test that valid config keys match default config keys."""
        assert VALID_CONFIG_KEYS == set(DEFAULT_CONFIG.keys())
    
    def test_env_prefix_constant(self):
        """Test environment variable prefix."""
        assert ENV_PREFIX == 'CACAO_PW_'
    
    def test_get_default_config(self):
        """Test get_default_config returns copy of defaults."""
        config = get_default_config()
        assert config == DEFAULT_CONFIG
        assert config is not DEFAULT_CONFIG  # Should be a copy
        
        # Modifying returned config shouldn't affect original
        config['minlen'] = 10
        assert DEFAULT_CONFIG['minlen'] == 6


class TestLoadConfig:
    """Test main configuration loading functionality."""
    
    def test_load_config_defaults_only(self):
        """Test loading config with no overrides returns defaults."""
        config = load_config()
        assert config == DEFAULT_CONFIG
        assert config is not DEFAULT_CONFIG  # Should be a copy
    
    def test_load_config_with_runtime_overrides(self):
        """Test runtime configuration overrides."""
        runtime_config = {
            'minlen': 8,
            'maxlen': 20,
            'minuchars': 2
        }
        config = load_config(runtime_config)
        
        # Overridden values should match
        assert config['minlen'] == 8
        assert config['maxlen'] == 20
        assert config['minuchars'] == 2
        
        # Non-overridden values should remain default
        assert config['minlchars'] == DEFAULT_CONFIG['minlchars']
        assert config['minnumbers'] == DEFAULT_CONFIG['minnumbers']
        assert config['minschars'] == DEFAULT_CONFIG['minschars']
    
    def test_load_config_with_empty_runtime_config(self):
        """Test loading config with empty runtime config."""
        config = load_config({})
        assert config == DEFAULT_CONFIG
    
    def test_load_config_runtime_config_none(self):
        """Test loading config with None runtime config."""
        config = load_config(None)
        assert config == DEFAULT_CONFIG
    
    @patch.dict(os.environ, {}, clear=True)
    def test_load_config_no_env_vars(self):
        """Test loading config with no environment variables set."""
        config = load_config()
        assert config == DEFAULT_CONFIG
    
    @patch.dict(os.environ, {
        'CACAO_PW_MINLEN': '10',
        'CACAO_PW_MAXLEN': '25',
        'CACAO_PW_MINUCHARS': '3'
    }, clear=True)
    def test_load_config_with_env_vars(self):
        """Test loading config with environment variables."""
        config = load_config()
        
        assert config['minlen'] == 10
        assert config['maxlen'] == 25
        assert config['minuchars'] == 3
        # Non-overridden should remain default
        assert config['minlchars'] == DEFAULT_CONFIG['minlchars']
        assert config['minnumbers'] == DEFAULT_CONFIG['minnumbers']
        assert config['minschars'] == DEFAULT_CONFIG['minschars']
    
    @patch.dict(os.environ, {
        'CACAO_PW_MINLEN': '12',
        'CACAO_PW_MAXLEN': '30'
    }, clear=True)
    def test_load_config_runtime_overrides_env_vars(self):
        """Test that runtime config overrides environment variables."""
        runtime_config = {
            'minlen': 15,  # Should override env var
            'minuchars': 4  # Should be used (no env var for this)
        }
        config = load_config(runtime_config)
        
        assert config['minlen'] == 15  # Runtime override
        assert config['maxlen'] == 30  # From env var
        assert config['minuchars'] == 4  # Runtime override
        # Defaults for the rest
        assert config['minlchars'] == DEFAULT_CONFIG['minlchars']
        assert config['minnumbers'] == DEFAULT_CONFIG['minnumbers']
        assert config['minschars'] == DEFAULT_CONFIG['minschars']
    
    @patch.dict(os.environ, {'CACAO_PW_MINLEN': 'invalid'}, clear=True)
    def test_load_config_invalid_env_var_value(self):
        """Test error handling for invalid environment variable values."""
        with pytest.raises(ValueError, match="Invalid value for CACAO_PW_MINLEN: invalid. Must be an integer."):
            load_config()
    
    @patch.dict(os.environ, {'CACAO_PW_MAXLEN': '12.5'}, clear=True)
    def test_load_config_float_env_var_value(self):
        """Test error handling for float environment variable values."""
        with pytest.raises(ValueError, match="Invalid value for CACAO_PW_MAXLEN: 12.5. Must be an integer."):
            load_config()
    
    def test_load_config_invalid_runtime_key(self):
        """Test error handling for invalid runtime configuration keys."""
        runtime_config = {
            'minlen': 8,
            'invalid_key': 10
        }
        with pytest.raises(ValueError, match="Invalid configuration keys: {'invalid_key'}"):
            load_config(runtime_config)
    
    def test_load_config_multiple_invalid_runtime_keys(self):
        """Test error handling for multiple invalid runtime configuration keys."""
        runtime_config = {
            'minlen': 8,
            'bad_key1': 10,
            'bad_key2': 5
        }
        with pytest.raises(ValueError, match="Invalid configuration keys:"):
            load_config(runtime_config)
    
    def test_load_config_invalid_runtime_value_type(self):
        """Test error handling for invalid runtime configuration value types."""
        runtime_config = {
            'minlen': '8'  # String instead of int
        }
        with pytest.raises(ValueError, match="Configuration value for 'minlen' must be an integer, got: 8"):
            load_config(runtime_config)
    
    def test_load_config_invalid_runtime_value_negative(self):
        """Test error handling for invalid negative runtime values."""
        runtime_config = {
            'minlen': -5  # Less than -1
        }
        with pytest.raises(ValueError, match="Configuration value for 'minlen' must be >= -1, got: -5"):
            load_config(runtime_config)
    
    def test_load_config_allows_negative_one(self):
        """Test that -1 values are allowed (for CLI exclusion options)."""
        runtime_config = {
            'minuchars': -1,
            'minlchars': -1,
            'minnumbers': -1,
            'minschars': -1
        }
        config = load_config(runtime_config)
        assert config['minuchars'] == -1
        assert config['minlchars'] == -1
        assert config['minnumbers'] == -1
        assert config['minschars'] == -1


class TestConfigValidation:
    """Test configuration validation logic."""
    
    def test_validate_config_valid(self):
        """Test validation passes for valid config."""
        valid_config = {
            'minlen': 8,
            'maxlen': 16,
            'minuchars': 2,
            'minlchars': 2,
            'minnumbers': 2,
            'minschars': 2
        }
        # Should not raise any exception
        _validate_config(valid_config)
    
    def test_validate_config_minlen_greater_than_maxlen(self):
        """Test validation fails when minlen > maxlen."""
        invalid_config = DEFAULT_CONFIG.copy()
        invalid_config['minlen'] = 20
        invalid_config['maxlen'] = 10
        
        with pytest.raises(ValueError, match="minlen \\(20\\) cannot be greater than maxlen \\(10\\)"):
            _validate_config(invalid_config)
    
    def test_validate_config_min_chars_exceed_maxlen(self):
        """Test validation fails when sum of min chars exceeds maxlen."""
        invalid_config = {
            'minlen': 6,
            'maxlen': 8,
            'minuchars': 3,
            'minlchars': 3,
            'minnumbers': 3,
            'minschars': 3  # Total: 12 > maxlen: 8
        }
        
        with pytest.raises(ValueError, match="Sum of minimum character requirements \\(12\\) cannot exceed maxlen \\(8\\)"):
            _validate_config(invalid_config)
    
    def test_validate_config_edge_case_requirements_equal_maxlen(self):
        """Test validation passes when min char requirements equal maxlen."""
        edge_config = {
            'minlen': 6,
            'maxlen': 8,
            'minuchars': 2,
            'minlchars': 2,
            'minnumbers': 2,
            'minschars': 2  # Total: 8 = maxlen: 8
        }
        # Should not raise any exception
        _validate_config(edge_config)
    
    def test_validate_config_requirements_exceed_minlen(self):
        """Test validation allows requirements to exceed minlen (warning case)."""
        warning_config = {
            'minlen': 4,  # Small minlen
            'maxlen': 16,
            'minuchars': 2,
            'minlchars': 2,
            'minnumbers': 2,
            'minschars': 2  # Total: 8 > minlen: 4
        }
        # Should not raise any exception - this is allowed
        _validate_config(warning_config)


class TestGetConfigFromEnv:
    """Test environment-only configuration loading."""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_config_from_env_no_vars(self):
        """Test getting config from env with no variables set."""
        config = get_config_from_env()
        assert config == DEFAULT_CONFIG
    
    @patch.dict(os.environ, {
        'CACAO_PW_MINLEN': '12',
        'CACAO_PW_MAXLEN': '24',
        'CACAO_PW_MINUCHARS': '2'
    }, clear=True)
    def test_get_config_from_env_with_vars(self):
        """Test getting config from environment variables."""
        config = get_config_from_env()
        
        assert config['minlen'] == 12
        assert config['maxlen'] == 24
        assert config['minuchars'] == 2
        # Defaults for unset variables
        assert config['minlchars'] == DEFAULT_CONFIG['minlchars']
        assert config['minnumbers'] == DEFAULT_CONFIG['minnumbers']
        assert config['minschars'] == DEFAULT_CONFIG['minschars']
    
    @patch.dict(os.environ, {'CACAO_PW_MINLEN': 'bad_value'}, clear=True)
    def test_get_config_from_env_invalid_value(self):
        """Test error handling in get_config_from_env."""
        with pytest.raises(ValueError, match="Invalid value for CACAO_PW_MINLEN: bad_value"):
            get_config_from_env()


class TestConfigIntegration:
    """Integration tests for configuration functionality."""
    
    def test_full_config_precedence_chain(self):
        """Test the complete precedence chain: runtime > env > defaults."""
        # Set up environment variables
        with patch.dict(os.environ, {
            'CACAO_PW_MINLEN': '10',
            'CACAO_PW_MAXLEN': '20',
            'CACAO_PW_MINUCHARS': '3',
            'CACAO_PW_MINLCHARS': '3'
        }, clear=True):
            # Runtime config overrides some env vars
            runtime_config = {
                'minlen': 12,  # Override env var
                'minnumbers': 4  # New value (no env var)
                # maxlen, minuchars, minlchars should come from env
                # minschars should come from default
            }
            
            config = load_config(runtime_config)
            
            assert config['minlen'] == 12      # Runtime override
            assert config['maxlen'] == 20      # From env var
            assert config['minuchars'] == 3    # From env var
            assert config['minlchars'] == 3    # From env var
            assert config['minnumbers'] == 4   # Runtime override
            assert config['minschars'] == 1    # Default value
    
    def test_config_with_all_zeros(self):
        """Test configuration with all zero minimum requirements."""
        zero_config = {
            'minlen': 1,
            'maxlen': 10,
            'minuchars': 0,
            'minlchars': 0,
            'minnumbers': 0,
            'minschars': 0
        }
        config = load_config(zero_config)
        assert config['minuchars'] == 0
        assert config['minlchars'] == 0
        assert config['minnumbers'] == 0
        assert config['minschars'] == 0
    
    def test_config_boundary_values(self):
        """Test configuration with boundary values."""
        boundary_config = {
            'minlen': 1,
            'maxlen': 1000,
            'minuchars': 0,
            'minlchars': 0,
            'minnumbers': 0,
            'minschars': 1
        }
        config = load_config(boundary_config)
        assert config['minlen'] == 1
        assert config['maxlen'] == 1000
        assert config['minschars'] == 1
    
    @patch.dict(os.environ, {
        'CACAO_PW_MINLEN': '0',
        'CACAO_PW_MAXLEN': '0'
    }, clear=True)
    def test_config_zero_lengths_from_env(self):
        """Test handling zero lengths from environment variables."""
        with pytest.raises(ValueError, match="minlen \\(0\\) cannot be greater than maxlen \\(0\\)"):
            load_config()
    
    def test_config_immutability(self):
        """Test that returned config is independent of sources."""
        original_default = DEFAULT_CONFIG.copy()
        
        # Load config and modify it
        config = load_config()
        config['minlen'] = 999
        
        # Original should be unchanged
        assert DEFAULT_CONFIG == original_default
        
        # Loading again should give fresh copy
        new_config = load_config()
        assert new_config['minlen'] == original_default['minlen']


class TestConfigErrorMessages:
    """Test error message quality and specificity."""
    
    def test_invalid_key_error_message_clarity(self):
        """Test that invalid key error messages are clear and helpful."""
        runtime_config = {'bad_key': 5}
        
        with pytest.raises(ValueError) as exc_info:
            load_config(runtime_config)
        
        error_msg = str(exc_info.value)
        assert 'bad_key' in error_msg
        assert 'Valid keys are:' in error_msg
        assert all(key in error_msg for key in VALID_CONFIG_KEYS)
    
    def test_validation_error_message_includes_values(self):
        """Test that validation error messages include actual values."""
        invalid_config = {'minlen': 25, 'maxlen': 10}
        
        with pytest.raises(ValueError) as exc_info:
            load_config(invalid_config)
        
        error_msg = str(exc_info.value)
        assert '25' in error_msg
        assert '10' in error_msg
    
    def test_char_requirements_error_includes_calculation(self):
        """Test that character requirements error shows the calculation."""
        invalid_config = {
            'minlen': 6,
            'maxlen': 5,
            'minuchars': 2,
            'minlchars': 2,
            'minnumbers': 2,
            'minschars': 2
        }
        
        with pytest.raises(ValueError) as exc_info:
            load_config(invalid_config)
        
        error_msg = str(exc_info.value)
        # Should show sum (8) and maxlen (5)
        assert '8' in error_msg  # Sum of requirements
        assert '5' in error_msg  # maxlen value