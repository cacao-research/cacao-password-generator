#!/usr/bin/env python3
"""
Command Line Interface for cacao-password-generator.

This module provides the `cacao-pass` command-line tool for secure password
generation with configurable constraints and strength rating.
"""

import argparse
import json
import sys
import platform
from typing import Dict, Any, Optional, List, Tuple

from . import generate, validate, rating, get_version, get_default_config
from .rating import detailed_rating


# Shell metacharacters that commonly cause parsing issues
SHELL_METACHARACTERS = {
    '|': 'pipe',
    '&': 'ampersand',
    '<': 'less-than',
    '>': 'greater-than',
    '(': 'open-parenthesis',
    ')': 'close-parenthesis',
    ';': 'semicolon',
    '"': 'double-quote',
    "'": 'single-quote',
    '`': 'backtick',
    '$': 'dollar-sign',
    '\\': 'backslash',
    '*': 'asterisk',
    '?': 'question-mark',
    '[': 'open-bracket',
    ']': 'close-bracket',
    '{': 'open-brace',
    '}': 'close-brace',
    '~': 'tilde',
    '^': 'caret'
}


def detect_shell_metacharacters(password: str) -> List[Tuple[str, str]]:
    """
    Detect shell metacharacters in a password that could cause parsing issues.
    
    Args:
        password: Password string to analyze
        
    Returns:
        List of tuples containing (character, description) for found metacharacters
    """
    found_chars = []
    for char in password:
        if char in SHELL_METACHARACTERS:
            found_chars.append((char, SHELL_METACHARACTERS[char]))
    return found_chars


def is_likely_truncated_password(password: str) -> bool:
    """
    Check if a password appears to be truncated due to shell parsing.
    
    Common patterns for truncated passwords:
    - Ends abruptly after a shell metacharacter
    - Very short compared to typical secure passwords
    - Ends with common shell command starters
    
    Args:
        password: Password string to analyze
        
    Returns:
        True if password appears truncated, False otherwise
    """
    if not password:
        return True
    
    # Check for abrupt ending after metacharacters
    if len(password) < 8 and any(char in SHELL_METACHARACTERS for char in password):
        return True
    
    # Check for common shell command patterns at the end
    shell_command_patterns = [
        'm:', 'uSg', 'ls', 'dir', 'cat', 'echo', 'cd', 'rm', 'mv', 'cp'
    ]
    
    for pattern in shell_command_patterns:
        if password.endswith(pattern):
            return True
    
    return False


def get_shell_specific_quoting_help() -> str:
    """
    Generate shell-specific quoting help based on the current platform.
    
    Returns:
        Formatted help text with shell-specific examples
    """
    system = platform.system().lower()
    
    help_text = """
Shell Quoting Help
==================

Your password contains special characters that may cause shell parsing issues.
Here's how to properly quote passwords in different shells:

"""
    
    if system == 'windows':
        help_text += """Windows Command Prompt (CMD):
  Use double quotes around the entire password:
  cacao-pass --rating-only "your|password"
  cacao-pass --rating "pass&word"

Windows PowerShell:
  Use single quotes (preferred) or double quotes:
  cacao-pass --rating-only 'your|password'
  cacao-pass --rating "pass&word"

"""
    else:
        help_text += """Bash/Zsh/Unix Shells:
  Use single quotes (safest - prevents all expansion):
  cacao-pass --rating-only 'your|password'
  cacao-pass --rating 'pass$word'

  Or use double quotes (allows variable expansion):
  cacao-pass --rating-only "your|password"

"""
    
    help_text += """Git Bash on Windows:
  Use single quotes like Unix shells:
  cacao-pass --rating-only 'your|password'

Common Problematic Characters:
  | & < > ( ) ; " ' ` $ \\ * ? [ ] { } ~ ^

Tips:
  1. Always quote passwords containing special characters
  2. Single quotes are generally safer than double quotes
  3. If using double quotes, be careful with $ ` \\ characters
  4. Test your command in a safe environment first
"""
    
    return help_text


def validate_password_for_shell_issues(password: str, original_input: str = "") -> Optional[str]:
    """
    Validate password for potential shell parsing issues and return error message if found.
    
    Args:
        password: The password that was parsed
        original_input: The original input if available
        
    Returns:
        Error message string if issues detected, None if password appears valid
    """
    if not password:
        return "Password is empty. This may indicate shell parsing issues."
    
    # Check for likely truncation
    if is_likely_truncated_password(password):
        metacharacters = detect_shell_metacharacters(original_input or password)
        
        if metacharacters:
            char_list = ", ".join([f"'{char}' ({desc})" for char, desc in metacharacters])
            return f"Password appears truncated due to shell metacharacters: {char_list}"
    
    # Check for metacharacters that might cause issues
    metacharacters = detect_shell_metacharacters(password)
    if metacharacters:
        char_list = ", ".join([f"'{char}'" for char, _ in metacharacters])
        
        # Only warn for high-risk characters or if password seems suspiciously short
        high_risk_chars = {'|', '&', '<', '>', ';', '`', '$'}
        has_high_risk = any(char in high_risk_chars for char, _ in metacharacters)
        
        if has_high_risk or len(password) < 8:
            return f"Password contains shell metacharacters that may cause parsing issues: {char_list}"
    
    return None


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for the CLI.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='cacao-pass',
        description='Generate secure passwords with configurable constraints and strength rating',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cacao-pass                           Generate with defaults
  cacao-pass -l 20                     Override length to 20 characters
  cacao-pass --no-symbols              Exclude symbols from generation
  cacao-pass --minlen 12 --maxlen 24   Set length range 12-24 characters
  cacao-pass --min-upper 2 --min-symbols 3  Require 2+ uppercase, 3+ symbols
  cacao-pass --rating-only "MyPassword123!"  Rate an existing password
  cacao-pass --multiple 5              Generate 5 passwords
  cacao-pass --config-info             Show current configuration
        """
    )
    
    # Version information
    parser.add_argument(
        '--version', '-v',
        action='version',
        version=f'cacao-pass {get_version()}'
    )
    
    # Primary action group - mutually exclusive
    action_group = parser.add_mutually_exclusive_group()
    
    action_group.add_argument(
        '--rating-only', '-r',
        metavar='PASSWORD',
        help='Rate the strength of an existing password without generating a new one'
    )
    
    action_group.add_argument(
        '--rating',
        metavar='PASSWORD',
        help='Show only the password rating (e.g., "strong")'
    )
    
    action_group.add_argument(
        '--stats',
        metavar='PASSWORD',
        help='Show key password metrics in human-readable format'
    )
    
    action_group.add_argument(
        '--json',
        metavar='PASSWORD',
        help='Show full password analysis as JSON'
    )
    
    action_group.add_argument(
        '--suggestions',
        metavar='PASSWORD',
        help='Show only password improvement suggestions'
    )
    
    action_group.add_argument(
        '--all',
        metavar='PASSWORD',
        help='Show all available password analysis formats'
    )
    
    action_group.add_argument(
        '--config-info', '-c',
        action='store_true',
        help='Show current default configuration and exit'
    )
    
    action_group.add_argument(
        '--help-quoting',
        action='store_true',
        help='Show help for properly quoting passwords with special characters'
    )
    
    # Password generation options
    gen_group = parser.add_argument_group('Password Generation Options')
    
    gen_group.add_argument(
        '--length', '-l',
        type=int,
        metavar='N',
        help='Override password length (must be positive integer)'
    )
    
    gen_group.add_argument(
        '--multiple', '-m',
        type=int,
        metavar='COUNT',
        default=1,
        help='Generate multiple passwords (default: 1)'
    )
    
    # Length constraint options
    length_group = parser.add_argument_group('Length Constraints')
    
    length_group.add_argument(
        '--minlen',
        type=int,
        metavar='N',
        help='Minimum password length'
    )
    
    length_group.add_argument(
        '--maxlen',
        type=int,
        metavar='N',
        help='Maximum password length'
    )
    
    # Character requirement options
    char_req_group = parser.add_argument_group('Character Requirements')
    
    char_req_group.add_argument(
        '--min-upper',
        type=int,
        metavar='N',
        help='Minimum number of uppercase characters'
    )
    
    char_req_group.add_argument(
        '--min-lower',
        type=int,
        metavar='N',
        help='Minimum number of lowercase characters'
    )
    
    char_req_group.add_argument(
        '--min-numbers',
        type=int,
        metavar='N',
        help='Minimum number of numeric characters'
    )
    
    char_req_group.add_argument(
        '--min-symbols',
        type=int,
        metavar='N',
        help='Minimum number of symbol characters'
    )
    
    # Character exclusion options
    exclusion_group = parser.add_argument_group('Character Exclusions')
    
    exclusion_group.add_argument(
        '--no-uppercase',
        action='store_true',
        help='Exclude uppercase characters (sets min-upper to 0)'
    )
    
    exclusion_group.add_argument(
        '--no-lowercase',
        action='store_true',
        help='Exclude lowercase characters (sets min-lower to 0)'
    )
    
    exclusion_group.add_argument(
        '--no-numbers',
        action='store_true',
        help='Exclude numeric characters (sets min-numbers to 0)'
    )
    
    exclusion_group.add_argument(
        '--no-symbols',
        action='store_true',
        help='Exclude symbol characters (sets min-symbols to 0)'
    )
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    
    output_group.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Only output the password(s), no additional information'
    )
    
    output_group.add_argument(
        '--no-rating',
        action='store_true',
        help='Skip strength rating output'
    )
    
    return parser


def build_config_from_args(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Build configuration dictionary from command line arguments.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Configuration dictionary for password generation
        
    Raises:
        ValueError: If arguments result in invalid configuration
    """
    config = {}
    
    # Length constraints
    if args.minlen is not None:
        if args.minlen <= 0:
            raise ValueError("--minlen must be a positive integer")
        config['minlen'] = args.minlen
    
    if args.maxlen is not None:
        if args.maxlen <= 0:
            raise ValueError("--maxlen must be a positive integer")
        config['maxlen'] = args.maxlen
    
    # Character requirements - handle exclusions using negative values
    if args.no_uppercase or args.min_upper is not None:
        config['minuchars'] = -1 if args.no_uppercase else args.min_upper
    
    if args.no_lowercase or args.min_lower is not None:
        config['minlchars'] = -1 if args.no_lowercase else args.min_lower
    
    if args.no_numbers or args.min_numbers is not None:
        config['minnumbers'] = -1 if args.no_numbers else args.min_numbers
    
    if args.no_symbols or args.min_symbols is not None:
        config['minschars'] = -1 if args.no_symbols else args.min_symbols
    
    # Validate character requirements (allow negative values for exclusion)
    for key, value in config.items():
        if key.startswith('min') and value is not None and value < -1:
            raise ValueError(f"Character requirement {key} must be >= -1")
    
    return config


def validate_args(args: argparse.Namespace) -> None:
    """
    Validate argument combinations for logical consistency.
    
    Args:
        args: Parsed command line arguments
        
    Raises:
        ValueError: If argument combination is invalid
    """
    # Check multiple passwords argument
    if args.multiple is not None and args.multiple <= 0:
        raise ValueError("--multiple must be a positive integer")
    
    # Check length argument
    if args.length is not None and args.length <= 0:
        raise ValueError("--length must be a positive integer")
    
    # Check that exclusion and requirement aren't both specified for same type
    exclusion_conflicts = [
        (args.no_uppercase, args.min_upper, "uppercase"),
        (args.no_lowercase, args.min_lower, "lowercase"), 
        (args.no_numbers, args.min_numbers, "numbers"),
        (args.no_symbols, args.min_symbols, "symbols")
    ]
    
    for exclude_flag, min_requirement, char_type in exclusion_conflicts:
        if exclude_flag and min_requirement is not None and min_requirement > 0:
            raise ValueError(
                f"Cannot both exclude {char_type} (--no-{char_type}) and "
                f"require minimum {char_type} (--min-{char_type})"
            )


def show_config_info() -> None:
    """Show current default configuration information."""
    config = get_default_config()
    
    print("Cacao Password Generator - Default Configuration")
    print("=" * 50)
    print(f"Minimum length: {config['minlen']}")
    print(f"Maximum length: {config['maxlen']}")
    print(f"Minimum uppercase: {config['minuchars']}")
    print(f"Minimum lowercase: {config['minlchars']}")
    print(f"Minimum numbers: {config['minnumbers']}")
    print(f"Minimum symbols: {config['minschars']}")
    print()
    print("Environment variables (if set) can override these defaults:")
    print("  CACAO_PW_MINLEN, CACAO_PW_MAXLEN")
    print("  CACAO_PW_MINUCHARS, CACAO_PW_MINLCHARS")
    print("  CACAO_PW_MINNUMBERS, CACAO_PW_MINSCHARS")


def rate_password(password: str, quiet: bool = False) -> str:
    """
    Rate a password and return formatted output using enhanced analysis.
    
    Args:
        password: Password to rate
        quiet: If True, return only the enhanced analysis without extra formatting
        
    Returns:
        Formatted rating information with crack time estimation
    """
    # Get detailed analysis
    detailed_analysis = detailed_rating(password)
    
    # Validation analysis
    is_valid, errors = validate(password)
    
    output = []
    
    if not quiet:
        # Enhanced format with title and description
        output.append("Password strength analyser")
        output.append("")
        output.append("Discover the strength of your password with this client-side-only password strength analyser and crack time estimation tool.")
        output.append(password)
        output.append("")
    
    # Core analysis information
    output.append("Duration to crack this password with brute force")
    output.append(detailed_analysis['crack_time_formatted'])
    output.append(f"Password length:")
    output.append(str(detailed_analysis['length_analysis']['length']))
    output.append(f"Entropy:")
    output.append(str(detailed_analysis['entropy']))
    output.append(f"Character set size:")
    output.append(str(detailed_analysis['character_set_size']))
    output.append(f"Score:")
    output.append(f"{detailed_analysis['password_score']} / 100")
    
    if not quiet:
        # Add validation information if there are issues
        if not is_valid:
            output.append("")
            output.append("Validation: FAILED")
            for error in errors:
                output.append(f"  - {error}")
        else:
            output.append("")
            output.append("Validation: PASSED")
    
    return "\n".join(output)


def handle_rating_only_output(password: str) -> str:
    """
    Handle --rating option: output only the rating string.
    
    Args:
        password: Password to rate
        
    Returns:
        Just the rating string (e.g., "strong")
    """
    if not password:
        return "weak"
    
    detailed_analysis = detailed_rating(password)
    return detailed_analysis['rating']


def handle_stats_output(password: str) -> str:
    """
    Handle --stats option: output key metrics in human-readable format.
    
    Args:
        password: Password to rate
        
    Returns:
        Human-readable key metrics
    """
    if not password:
        return "Password is empty"
    
    detailed_analysis = detailed_rating(password)
    
    output = []
    output.append(f"Rating: {detailed_analysis['rating']}")
    output.append(f"Length: {detailed_analysis['length_analysis']['length']}")
    output.append(f"Entropy: {detailed_analysis['entropy']} bits")
    output.append(f"Character Set Size: {detailed_analysis['character_set_size']}")
    output.append(f"Score: {detailed_analysis['password_score']}/100")
    output.append(f"Crack Time: {detailed_analysis['crack_time_formatted']}")
    output.append(f"Character Types: {detailed_analysis['character_analysis']['types_present']}")
    output.append(f"Diversity Level: {detailed_analysis['character_analysis']['diversity_level']}")
    
    return "\n".join(output)


def handle_json_output(password: str) -> str:
    """
    Handle --json option: output the full JSON structure.
    
    Args:
        password: Password to rate
        
    Returns:
        Pretty-printed JSON string
    """
    if not password:
        return json.dumps({'error': 'Password is empty'}, indent=2)
    
    detailed_analysis = detailed_rating(password)
    return json.dumps(detailed_analysis, indent=2)


def handle_suggestions_output(password: str) -> str:
    """
    Handle --suggestions option: output only improvement suggestions.
    
    Args:
        password: Password to rate
        
    Returns:
        Bulleted list of suggestions
    """
    if not password:
        return "• Password is empty or invalid"
    
    detailed_analysis = detailed_rating(password)
    suggestions = detailed_analysis.get('suggestions', [])
    
    if not suggestions:
        return "• No suggestions - password looks good!"
    
    return "\n".join(f"• {suggestion}" for suggestion in suggestions)


def handle_all_output(password: str) -> str:
    """
    Handle --all option: output all available formats.
    
    Args:
        password: Password to rate
        
    Returns:
        All formats separated by clear headers
    """
    if not password:
        return "Password is empty - no analysis available"
    
    output = []
    
    # Rating
    output.append("=== RATING ===")
    output.append(handle_rating_only_output(password))
    output.append("")
    
    # Stats
    output.append("=== STATISTICS ===")
    output.append(handle_stats_output(password))
    output.append("")
    
    # Suggestions
    output.append("=== SUGGESTIONS ===")
    output.append(handle_suggestions_output(password))
    output.append("")
    
    # JSON
    output.append("=== JSON DATA ===")
    output.append(handle_json_output(password))
    
    return "\n".join(output)


def generate_and_display_passwords(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """
    Generate and display password(s) based on arguments.
    
    Args:
        args: Parsed command line arguments
        config: Configuration dictionary
    """
    try:
        # Generate passwords
        if args.multiple == 1:
            password = generate(config, length=args.length)
            passwords = [password]
        else:
            from . import generate_multiple
            passwords = generate_multiple(args.multiple, config, length=args.length)
        
        # Display results
        for i, password in enumerate(passwords, 1):
            if args.quiet:
                print(password)
            else:
                if args.multiple > 1:
                    print(f"Password {i}: {password}")
                else:
                    print(f"Generated Password: {password}")
                
                if not args.no_rating:
                    strength_rating = rating(password)
                    print(f"Strength Rating: {strength_rating}")
                
                if args.multiple > 1 and i < len(passwords):
                    print()  # Blank line between multiple passwords
    
    except Exception as e:
        print(f"Error generating password: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Validate arguments
        validate_args(args)
        
        # Handle special actions first
        if args.config_info:
            show_config_info()
            return
        
        if args.help_quoting:
            print(get_shell_specific_quoting_help())
            return
        
        if args.rating_only:
            # Validate password for shell parsing issues
            shell_error = validate_password_for_shell_issues(args.rating_only)
            if shell_error:
                print(f"Error: {shell_error}", file=sys.stderr)
                print("\nFor help with shell quoting, run: cacao-pass --help-quoting", file=sys.stderr)
                sys.exit(1)
            
            result = rate_password(args.rating_only, args.quiet)
            print(result)
            return
        
        # Handle new rating options with enhanced shell validation
        if args.rating:
            if not args.rating.strip():
                print("Error: Password cannot be empty", file=sys.stderr)
                sys.exit(1)
            
            shell_error = validate_password_for_shell_issues(args.rating)
            if shell_error:
                print(f"Warning: {shell_error}", file=sys.stderr)
                print("For help with shell quoting, run: cacao-pass --help-quoting", file=sys.stderr)
                print()  # Add blank line before output
            
            result = handle_rating_only_output(args.rating)
            print(result)
            return
        
        if args.stats:
            if not args.stats.strip():
                print("Error: Password cannot be empty", file=sys.stderr)
                sys.exit(1)
            
            shell_error = validate_password_for_shell_issues(args.stats)
            if shell_error:
                print(f"Warning: {shell_error}", file=sys.stderr)
                print("For help with shell quoting, run: cacao-pass --help-quoting", file=sys.stderr)
                print()  # Add blank line before output
            
            result = handle_stats_output(args.stats)
            print(result)
            return
        
        if args.json:
            if not args.json.strip():
                print("Error: Password cannot be empty", file=sys.stderr)
                sys.exit(1)
            
            shell_error = validate_password_for_shell_issues(args.json)
            if shell_error:
                print(f"Warning: {shell_error}", file=sys.stderr)
                print("For help with shell quoting, run: cacao-pass --help-quoting", file=sys.stderr)
                print()  # Add blank line before output
            
            result = handle_json_output(args.json)
            print(result)
            return
        
        if args.suggestions:
            if not args.suggestions.strip():
                print("Error: Password cannot be empty", file=sys.stderr)
                sys.exit(1)
            
            shell_error = validate_password_for_shell_issues(args.suggestions)
            if shell_error:
                print(f"Warning: {shell_error}", file=sys.stderr)
                print("For help with shell quoting, run: cacao-pass --help-quoting", file=sys.stderr)
                print()  # Add blank line before output
            
            result = handle_suggestions_output(args.suggestions)
            print(result)
            return
        
        if args.all:
            if not args.all.strip():
                print("Error: Password cannot be empty", file=sys.stderr)
                sys.exit(1)
            
            shell_error = validate_password_for_shell_issues(args.all)
            if shell_error:
                print(f"Warning: {shell_error}", file=sys.stderr)
                print("For help with shell quoting, run: cacao-pass --help-quoting", file=sys.stderr)
                print()  # Add blank line before output
            
            result = handle_all_output(args.all)
            print(result)
            return
        
        # Build configuration from arguments
        config = build_config_from_args(args)
        
        # Generate and display passwords
        generate_and_display_passwords(args, config)
    
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()