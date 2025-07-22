#!/usr/bin/env python3
"""
Comprehensive test suite for cacao_password_generator.cli module.

This module tests the command-line interface functionality including:
- Argument parsing and validation
- Configuration building from CLI arguments  
- Output formatting and display functions
- CLI integration via subprocess
- Error handling and edge cases
"""

import pytest
import argparse
import sys
import subprocess
import json
import os
from io import StringIO
from unittest.mock import patch, MagicMock, call
from typing import Dict, Any, List

from cacao_password_generator.cli import (
    create_parser,
    build_config_from_args,
    validate_args,
    show_config_info,
    rate_password,
    generate_and_display_passwords,
    main
)


class TestArgumentParserCreation:
    """Test argument parser creation and basic functionality."""
    
    def test_create_parser_returns_parser(self):
        """Test that create_parser returns an ArgumentParser instance."""
        parser = create_parser()
        assert isinstance(parser, argparse.ArgumentParser)
        assert parser.prog == 'cacao-pass'
    
    def test_parser_has_version_action(self):
        """Test that parser includes version action."""
        parser = create_parser()
        
        # Test version argument parsing
        with pytest.raises(SystemExit) as excinfo:
            with patch('sys.stdout', new_callable=StringIO):
                parser.parse_args(['--version'])
        
        assert excinfo.value.code == 0
    
    def test_parser_has_help_text(self):
        """Test that parser includes comprehensive help text."""
        parser = create_parser()
        help_text = parser.format_help()
        
        # Check for key sections in help text
        assert 'Generate secure passwords' in help_text
        assert 'Examples:' in help_text
        assert 'Password Generation Options' in help_text
        assert 'Length Constraints' in help_text
        assert 'Character Requirements' in help_text
        assert 'Character Exclusions' in help_text
        assert 'Output Options' in help_text
    
    def test_parser_mutually_exclusive_actions(self):
        """Test that rating-only and config-info are mutually exclusive."""
        parser = create_parser()
        
        # Should work with either option alone
        args1 = parser.parse_args(['--rating-only', 'test123'])
        assert args1.rating_only == 'test123'
        
        args2 = parser.parse_args(['--config-info'])
        assert args2.config_info is True
        
        # Should fail with both options
        with pytest.raises(SystemExit):
            with patch('sys.stderr', new_callable=StringIO):
                parser.parse_args(['--rating-only', 'test', '--config-info'])


class TestArgumentParsing:
    """Test parsing of various argument combinations."""
    
    def test_parse_default_args(self):
        """Test parsing with no arguments (defaults)."""
        parser = create_parser()
        args = parser.parse_args([])
        
        assert args.length is None
        assert args.multiple == 1
        assert args.minlen is None
        assert args.maxlen is None
        assert args.min_upper is None
        assert args.min_lower is None
        assert args.min_numbers is None
        assert args.min_symbols is None
        assert args.no_uppercase is False
        assert args.no_lowercase is False
        assert args.no_numbers is False
        assert args.no_symbols is False
        assert args.quiet is False
        assert args.no_rating is False
        assert args.rating_only is None
        assert args.config_info is False
    
    def test_parse_length_argument(self):
        """Test parsing length argument."""
        parser = create_parser()
        
        args = parser.parse_args(['-l', '20'])
        assert args.length == 20
        
        args = parser.parse_args(['--length', '15'])
        assert args.length == 15
    
    def test_parse_multiple_argument(self):
        """Test parsing multiple passwords argument."""
        parser = create_parser()
        
        args = parser.parse_args(['-m', '5'])
        assert args.multiple == 5
        
        args = parser.parse_args(['--multiple', '3'])
        assert args.multiple == 3
    
    def test_parse_length_constraints(self):
        """Test parsing length constraint arguments."""
        parser = create_parser()
        args = parser.parse_args(['--minlen', '8', '--maxlen', '24'])
        
        assert args.minlen == 8
        assert args.maxlen == 24
    
    def test_parse_character_requirements(self):
        """Test parsing character requirement arguments."""
        parser = create_parser()
        args = parser.parse_args([
            '--min-upper', '2',
            '--min-lower', '3', 
            '--min-numbers', '1',
            '--min-symbols', '2'
        ])
        
        assert args.min_upper == 2
        assert args.min_lower == 3
        assert args.min_numbers == 1
        assert args.min_symbols == 2
    
    def test_parse_character_exclusions(self):
        """Test parsing character exclusion flags."""
        parser = create_parser()
        args = parser.parse_args([
            '--no-uppercase',
            '--no-lowercase', 
            '--no-numbers',
            '--no-symbols'
        ])
        
        assert args.no_uppercase is True
        assert args.no_lowercase is True
        assert args.no_numbers is True
        assert args.no_symbols is True
    
    def test_parse_output_options(self):
        """Test parsing output option flags."""
        parser = create_parser()
        args = parser.parse_args(['--quiet', '--no-rating'])
        
        assert args.quiet is True
        assert args.no_rating is True
    
    def test_parse_rating_only(self):
        """Test parsing rating-only mode."""
        parser = create_parser()
        args = parser.parse_args(['--rating-only', 'MyPassword123!'])
        
        assert args.rating_only == 'MyPassword123!'
    
    def test_parse_config_info(self):
        """Test parsing config-info flag."""
        parser = create_parser()
        args = parser.parse_args(['--config-info'])
        
        assert args.config_info is True


class TestConfigurationBuilding:
    """Test building configuration from parsed arguments."""
    
    def test_build_empty_config(self):
        """Test building config with no arguments."""
        parser = create_parser()
        args = parser.parse_args([])
        config = build_config_from_args(args)
        
        assert config == {}
    
    def test_build_config_with_length_constraints(self):
        """Test building config with length constraints."""
        parser = create_parser()
        args = parser.parse_args(['--minlen', '8', '--maxlen', '24'])
        config = build_config_from_args(args)
        
        assert config['minlen'] == 8
        assert config['maxlen'] == 24
    
    def test_build_config_with_character_requirements(self):
        """Test building config with character requirements."""
        parser = create_parser()
        args = parser.parse_args([
            '--min-upper', '2',
            '--min-lower', '3',
            '--min-numbers', '1', 
            '--min-symbols', '2'
        ])
        config = build_config_from_args(args)
        
        assert config['minuchars'] == 2
        assert config['minlchars'] == 3
        assert config['minnumbers'] == 1
        assert config['minschars'] == 2
    
    def test_build_config_with_exclusions(self):
        """Test building config with character exclusions."""
        parser = create_parser()
        args = parser.parse_args([
            '--no-uppercase',
            '--no-lowercase',
            '--no-numbers',
            '--no-symbols'
        ])
        config = build_config_from_args(args)
        
        assert config['minuchars'] == -1
        assert config['minlchars'] == -1
        assert config['minnumbers'] == -1
        assert config['minschars'] == -1
    
    def test_build_config_exclusion_overrides_requirement(self):
        """Test that exclusion flags override requirements."""
        parser = create_parser()
        args = parser.parse_args([
            '--min-upper', '2',
            '--no-uppercase'
        ])
        config = build_config_from_args(args)
        
        assert config['minuchars'] == -1
    
    def test_build_config_invalid_minlen(self):
        """Test error handling for invalid minlen."""
        parser = create_parser()
        args = parser.parse_args(['--minlen', '-1'])
        
        with pytest.raises(ValueError, match="--minlen must be a positive integer"):
            build_config_from_args(args)
    
    def test_build_config_invalid_maxlen(self):
        """Test error handling for invalid maxlen."""
        parser = create_parser()
        args = parser.parse_args(['--maxlen', '0'])
        
        with pytest.raises(ValueError, match="--maxlen must be a positive integer"):
            build_config_from_args(args)


class TestArgumentValidation:
    """Test validation of parsed arguments."""
    
    def test_validate_valid_args(self):
        """Test validation of valid arguments."""
        parser = create_parser()
        args = parser.parse_args(['--length', '16', '--multiple', '3'])
        
        # Should not raise any exception
        validate_args(args)
    
    def test_validate_invalid_multiple(self):
        """Test validation error for invalid multiple count."""
        parser = create_parser()
        args = parser.parse_args(['--multiple', '1'])
        args.multiple = 0  # Set invalid value manually
        
        with pytest.raises(ValueError, match="--multiple must be a positive integer"):
            validate_args(args)
    
    def test_validate_invalid_length(self):
        """Test validation error for invalid length."""
        parser = create_parser()
        args = parser.parse_args(['--length', '16'])
        args.length = -1  # Set invalid value manually
        
        with pytest.raises(ValueError, match="--length must be a positive integer"):
            validate_args(args)
    
    def test_validate_exclusion_requirement_conflict(self):
        """Test validation of exclusion and requirement conflicts."""
        parser = create_parser()
        
        # Test uppercase conflict
        args = parser.parse_args(['--no-uppercase', '--min-upper', '2'])
        with pytest.raises(ValueError, match="Cannot both exclude uppercase.*and require minimum uppercase"):
            validate_args(args)
        
        # Test lowercase conflict  
        args = parser.parse_args(['--no-lowercase', '--min-lower', '1'])
        with pytest.raises(ValueError, match="Cannot both exclude lowercase.*and require minimum lowercase"):
            validate_args(args)
        
        # Test numbers conflict
        args = parser.parse_args(['--no-numbers', '--min-numbers', '1'])
        with pytest.raises(ValueError, match="Cannot both exclude numbers.*and require minimum numbers"):
            validate_args(args)
        
        # Test symbols conflict
        args = parser.parse_args(['--no-symbols', '--min-symbols', '1'])
        with pytest.raises(ValueError, match="Cannot both exclude symbols.*and require minimum symbols"):
            validate_args(args)


class TestShowConfigInfo:
    """Test configuration information display."""
    
    @patch('cacao_password_generator.cli.get_default_config')
    @patch('builtins.print')
    def test_show_config_info(self, mock_print, mock_get_config):
        """Test showing configuration information."""
        mock_get_config.return_value = {
            'minlen': 8,
            'maxlen': 64,
            'minuchars': 1,
            'minlchars': 1,
            'minnumbers': 1,
            'minschars': 1
        }
        
        show_config_info()
        
        mock_get_config.assert_called_once()
        
        # Verify expected output calls
        print_calls = [call.args[0] if call.args else "" for call in mock_print.call_args_list]
        assert any("Cacao Password Generator" in call for call in print_calls)
        assert any("Minimum length: 8" in call for call in print_calls)
        assert any("Maximum length: 64" in call for call in print_calls)
        assert any("Environment variables" in call for call in print_calls)


class TestPasswordRating:
    """Test password rating functionality."""
    
    @patch('cacao_password_generator.cli.rating')
    @patch('cacao_password_generator.cli.validate')
    def test_rate_password_quiet_mode(self, mock_validate, mock_rating):
        """Test rating password in quiet mode."""
        mock_rating.return_value = "Strong"
        
        result = rate_password("test123", quiet=True)
        
        assert result == "Strong"
        mock_rating.assert_called_once_with("test123")
        mock_validate.assert_not_called()
    
    @patch('cacao_password_generator.cli.rating')
    @patch('cacao_password_generator.cli.validate')
    def test_rate_password_verbose_mode_valid(self, mock_validate, mock_rating):
        """Test rating password in verbose mode with valid password."""
        mock_rating.return_value = "Strong"
        mock_validate.return_value = (True, [])
        
        result = rate_password("TestPass123!")
        
        lines = result.split('\n')
        assert "Password: TestPass123!" in lines
        assert "Length: 12 characters" in lines
        assert "Strength: Strong" in lines
        assert "Validation: PASSED" in lines
        
        mock_rating.assert_called_once_with("TestPass123!")
        mock_validate.assert_called_once_with("TestPass123!")
    
    @patch('cacao_password_generator.cli.rating')
    @patch('cacao_password_generator.cli.validate')
    def test_rate_password_verbose_mode_invalid(self, mock_validate, mock_rating):
        """Test rating password in verbose mode with invalid password."""
        mock_rating.return_value = "Weak"
        mock_validate.return_value = (False, ["Password too short", "Missing uppercase"])
        
        result = rate_password("weak")
        
        lines = result.split('\n')
        assert "Password: weak" in lines
        assert "Length: 4 characters" in lines
        assert "Strength: Weak" in lines
        assert "Validation: FAILED" in lines
        assert "  - Password too short" in lines
        assert "  - Missing uppercase" in lines


class TestGenerateAndDisplayPasswords:
    """Test password generation and display functionality."""
    
    @patch('cacao_password_generator.cli.generate')
    @patch('cacao_password_generator.cli.rating')
    @patch('builtins.print')
    def test_generate_single_password_normal_mode(self, mock_print, mock_rating, mock_generate):
        """Test generating single password in normal mode."""
        mock_generate.return_value = "TestPass123!"
        mock_rating.return_value = "Strong"
        
        parser = create_parser()
        args = parser.parse_args([])
        config = {}
        
        generate_and_display_passwords(args, config)
        
        mock_generate.assert_called_once_with(config, length=None)
        mock_rating.assert_called_once_with("TestPass123!")
        
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert "Generated Password: TestPass123!" in print_calls
        assert "Strength Rating: Strong" in print_calls
    
    @patch('cacao_password_generator.cli.generate')
    @patch('builtins.print')
    def test_generate_single_password_quiet_mode(self, mock_print, mock_generate):
        """Test generating single password in quiet mode."""
        mock_generate.return_value = "TestPass123!"
        
        parser = create_parser()
        args = parser.parse_args(['--quiet'])
        config = {}
        
        generate_and_display_passwords(args, config)
        
        mock_print.assert_called_once_with("TestPass123!")
    
    @patch('cacao_password_generator.cli.generate')
    @patch('sys.exit')
    @patch('builtins.print')
    def test_generate_error_handling(self, mock_print, mock_exit, mock_generate):
        """Test error handling during password generation."""
        mock_generate.side_effect = ValueError("Invalid configuration")
        
        parser = create_parser()
        args = parser.parse_args([])
        config = {}
        
        generate_and_display_passwords(args, config)
        
        mock_exit.assert_called_once_with(1)
        # Check that error was printed to stderr
        assert mock_print.call_args_list[-1][1]['file'] == sys.stderr


class TestMainFunction:
    """Test main CLI entry point."""
    
    @patch('cacao_password_generator.cli.show_config_info')
    @patch('sys.argv', ['cacao-pass', '--config-info'])
    def test_main_config_info_mode(self, mock_show_config):
        """Test main function in config-info mode."""
        main()
        mock_show_config.assert_called_once()
    
    @patch('cacao_password_generator.cli.rate_password')
    @patch('builtins.print')
    @patch('sys.argv', ['cacao-pass', '--rating-only', 'TestPass123!'])
    def test_main_rating_only_mode(self, mock_print, mock_rate_password):
        """Test main function in rating-only mode."""
        mock_rate_password.return_value = "Password rating output"
        
        main()
        
        mock_rate_password.assert_called_once_with('TestPass123!', False)
        mock_print.assert_called_once_with("Password rating output")
    
    @patch('sys.exit')
    @patch('builtins.print')
    @patch('sys.argv', ['cacao-pass', '--length', '-1'])
    def test_main_validation_error(self, mock_print, mock_exit):
        """Test main function with validation error."""
        main()
        
        mock_exit.assert_called_once_with(1)
        assert any("Error:" in str(call) for call in mock_print.call_args_list)
    
    @patch('sys.exit')
    @patch('builtins.print')
    @patch('cacao_password_generator.cli.validate_args')
    @patch('sys.argv', ['cacao-pass'])
    def test_main_keyboard_interrupt(self, mock_validate, mock_print, mock_exit):
        """Test main function with KeyboardInterrupt."""
        mock_validate.side_effect = KeyboardInterrupt()
        
        main()
        
        mock_exit.assert_called_once_with(1)
        error_calls = [call for call in mock_print.call_args_list 
                      if call[1].get('file') == sys.stderr]
        assert any("Operation cancelled by user" in str(call) for call in error_calls)


class TestCLIIntegration:
    """Integration tests using subprocess to test the actual CLI."""
    
    def test_cli_help(self, cli_command):
        """Test CLI help output."""
        result = subprocess.run([*cli_command, '--help'], 
                              capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'Generate secure passwords' in result.stdout
        assert 'Examples:' in result.stdout
    
    def test_cli_version(self, cli_command):
        """Test CLI version output."""
        result = subprocess.run([*cli_command, '--version'], 
                              capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'cacao-pass' in result.stdout
    
    def test_cli_config_info(self, cli_command):
        """Test CLI config info output."""
        result = subprocess.run([*cli_command, '--config-info'], 
                              capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'Cacao Password Generator' in result.stdout
        assert 'Minimum length:' in result.stdout
        assert 'Maximum length:' in result.stdout
    
    def test_cli_basic_generation(self, cli_command):
        """Test basic password generation."""
        result = subprocess.run(cli_command, capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'Generated Password:' in result.stdout
        assert 'Strength Rating:' in result.stdout
    
    def test_cli_quiet_mode(self, cli_command):
        """Test CLI quiet mode."""
        result = subprocess.run([*cli_command, '--quiet'], 
                              capture_output=True, text=True)
        
        assert result.returncode == 0
        # In quiet mode, should only output the password
        lines = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        assert len(lines) == 1
        assert len(lines[0]) >= 8  # Should be at least minimum length
    
    def test_cli_rating_only_mode(self, cli_command):
        """Test CLI rating-only mode."""
        result = subprocess.run([*cli_command, '--rating-only', 'TestPassword123!'], 
                              capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'Password: TestPassword123!' in result.stdout
        assert 'Strength:' in result.stdout
        assert 'Validation:' in result.stdout
    
    @pytest.mark.slow
    def test_cli_multiple_generation(self, cli_command):
        """Test multiple password generation."""
        result = subprocess.run([*cli_command, '--multiple', '3'], 
                              capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'Password 1:' in result.stdout
        assert 'Password 2:' in result.stdout
        assert 'Password 3:' in result.stdout
    
    def test_cli_length_override(self, cli_command):
        """Test CLI with length override."""
        result = subprocess.run([*cli_command, '--length', '20', '--quiet'], 
                              capture_output=True, text=True)
        
        assert result.returncode == 0
        password = result.stdout.strip()
        assert len(password) == 20
    
    def test_cli_character_exclusions(self, cli_command):
        """Test CLI with character exclusions."""
        result = subprocess.run([*cli_command, '--no-symbols', '--quiet'], 
                              capture_output=True, text=True)
        
        assert result.returncode == 0
        password = result.stdout.strip()
        # Should not contain common symbols
        symbols = "!@#$%^&*()_+{}|:\"<>?[]\\;'.,/"
        assert not any(char in symbols for char in password)
    
    def test_cli_invalid_arguments(self, cli_command):
        """Test CLI error handling with invalid arguments."""
        result = subprocess.run([*cli_command, '--length', '-5'], 
                              capture_output=True, text=True)
        
        assert result.returncode == 1
        assert 'Error:' in result.stderr
    
    def test_cli_conflicting_arguments(self, cli_command):
        """Test CLI error handling with conflicting arguments."""
        result = subprocess.run([*cli_command, '--no-uppercase', '--min-upper', '2'], 
                              capture_output=True, text=True)
        
        assert result.returncode == 1
        assert 'Error:' in result.stderr