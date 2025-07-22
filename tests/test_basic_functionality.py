#!/usr/bin/env python3
"""
Basic functionality test for cacao-password-generator package.
This script tests the core API functions to ensure everything works correctly.
"""

import sys
import os

# Add src to Python path so we can import our package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import cacao_password_generator as cpg
    
    print("=== Cacao Password Generator - Basic Functionality Test ===\n")
    
    # Test 1: Package info
    print("1. Package Information:")
    info = cpg.get_package_info()
    print(f"   Name: {info['name']}")
    print(f"   Version: {info['version']}")
    print(f"   Description: {info['description']}")
    print(f"   Default config: {info['default_config']}")
    print()
    
    # Test 2: Basic password generation
    print("2. Basic Password Generation:")
    password1 = cpg.generate()
    print(f"   Generated password: {password1}")
    print(f"   Length: {len(password1)}")
    print()
    
    # Test 3: Password generation with specific length
    print("3. Password Generation with Specific Length:")
    password2 = cpg.generate(length=12)
    print(f"   Generated password (length=12): {password2}")
    print(f"   Actual length: {len(password2)}")
    print()
    
    # Test 4: Password generation with custom config
    print("4. Password Generation with Custom Config:")
    custom_config = {
        'minlen': 8,
        'maxlen': 10,
        'minuchars': 2,
        'minlchars': 2,
        'minnumbers': 1,
        'minschars': 1
    }
    password3 = cpg.generate(custom_config)
    print(f"   Generated password with custom config: {password3}")
    print(f"   Config used: {custom_config}")
    print()
    
    # Test 5: Password validation
    print("5. Password Validation:")
    test_passwords = [
        "Abc123!",      # Should be valid with default config
        "abc",          # Too short, no uppercase/numbers/special chars
        "ABCDEFGHIJ",   # No lowercase/numbers/special chars
        "MySecurePass1!" # Should be valid
    ]
    
    for test_pwd in test_passwords:
        is_valid, errors = cpg.validate(test_pwd)
        print(f"   Password: '{test_pwd}'")
        print(f"   Valid: {is_valid}")
        if errors:
            print(f"   Errors: {errors}")
        print()
    
    # Test 6: Password strength rating
    print("6. Password Strength Rating:")
    test_passwords_rating = [
        "123",                    # Should be weak
        "password",               # Should be weak
        "Password123",            # Should be medium/strong
        "MyS3cur3P@ssw0rd!2023"  # Should be strong/excellent
    ]
    
    for test_pwd in test_passwords_rating:
        strength = cpg.rating(test_pwd)
        print(f"   Password: '{test_pwd}' -> Rating: {strength}")
    print()
    
    # Test 7: Quick analysis
    print("7. Quick Analysis:")
    analysis = cpg.quick_analysis()
    print(f"   Generated password: {analysis['password']}")
    print(f"   Valid: {analysis['valid']}")
    print(f"   Rating: {analysis['rating']}")
    print(f"   Length: {analysis['length']}")
    print()
    
    # Test 8: Multiple password generation
    print("8. Multiple Password Generation:")
    passwords = cpg.generate_multiple(3, length=10)
    for i, pwd in enumerate(passwords, 1):
        print(f"   Password {i}: {pwd}")
    print()
    
    # Test 9: Detailed validation
    print("9. Detailed Validation:")
    detailed = cpg.validate_detailed("TestPass123!")
    print(f"   Password: TestPass123!")
    print(f"   Valid: {detailed['valid']}")
    print(f"   Character analysis: {detailed['analysis']}")
    print(f"   Length info: {detailed['length_info']}")
    print()
    
    # Test 10: Detailed rating
    print("10. Detailed Rating:")
    detailed_rating = cpg.detailed_rating("MyComplexP@ssw0rd!")
    print(f"   Password: MyComplexP@ssw0rd!")
    print(f"   Rating: {detailed_rating['rating']}")
    print(f"   Entropy: {detailed_rating['entropy']:.2f} bits")
    print(f"   Diversity score: {detailed_rating['diversity_score']}")
    print(f"   Suggestions: {detailed_rating['suggestions']}")
    
    print("\n=== All Tests Completed Successfully! ===")
    
except Exception as e:
    print(f"Error during testing: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)