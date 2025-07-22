# 🍫 Cacao Password Generator

**Generate secure, customizable passwords with confidence** 

[![PyPI version](https://badge.fury.io/py/cacao-password-generator.svg)](https://badge.fury.io/py/cacao-password-generator)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🚀 Quick Overview

Cacao Password Generator is a **secure, highly configurable Python package** for generating strong passwords with fine-grained control over character requirements. Whether you need a simple random password or one that meets specific security policies, Cacao has you covered.

✨ **Perfect for developers, security professionals, and anyone who takes password security seriously.**

---

## 🌟 Key Features

- 🔒 **Cryptographically Secure** - Uses Python's `secrets` module for true randomness
- ⚙️ **Highly Configurable** - Control length, character types, and minimum requirements
- 📊 **Integrated Strength Rating** - Built-in password strength assessment with entropy calculation
- 🛡️ **Shell Safety Aware** - Understands potentially problematic characters for shell environments
- 🔧 **Multiple Interfaces** - Use via CLI (`cacao-pass`) or Python API
- 🌐 **Environment Variable Support** - Configure defaults via `CACAO_PW_*` environment variables
- 📦 **Zero Dependencies** - No runtime dependencies, minimal footprint
- 🐍 **Modern Python** - Supports Python 3.8+

---

## 📦 Installation

Install from PyPI using pip:

```bash
pip install cacao-password-generator
```

---

## ⚡ Quick Start

### CLI Usage

Generate a secure password with default settings:

```bash
cacao-pass
```

Generate a custom password:

```bash
cacao-pass --length 16 --minuchars 2 --minlchars 2 --minnumbers 2 --minschars 2
```

### Python API Usage

```python
from cacao_password_generator.core import generate

# Simple generation
password = generate(length=12)
print(password)  # e.g., "Kp9$mL2@Wq3z"

# With custom constraints
password = generate({
    'minuchars': 3,
    'minlchars': 3,
    'minnumbers': 2,
    'minschars': 2
}, length=16)
```

---

## 📚 Detailed Usage

### 🖥️ Command Line Interface

The `cacao-pass` command provides a full-featured CLI:

```bash
# Basic usage with length
cacao-pass --length 20

# Full constraint specification
cacao-pass \
  --length 16 \
  --minuchars 2 \
  --minlchars 3 \
  --minnumbers 2 \
  --minschars 1

# Get help
cacao-pass --help
```

#### CLI Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--length` | `-l` | Password length | 12 |
| `--minuchars` | `-u` | Minimum uppercase letters | 1 |
| `--minlchars` | `-lc` | Minimum lowercase letters | 1 |
| `--minnumbers` | `-n` | Minimum numbers | 1 |
| `--minschars` | `-s` | Minimum special characters | 1 |

### 🐍 Python API

#### Basic Generation

```python
from cacao_password_generator.core import generate

# Default secure password (length 12)
password = generate()

# Custom length
password = generate(length=20)

# With character requirements
password = generate({
    'minuchars': 3, # At least 3 uppercase
    'minlchars': 3,  # At least 3 lowercase
    'minnumbers': 2, # At least 2 numbers
    'minschars': 2   # At least 2 special chars
}, length=16)


```

#### Advanced Usage with Validation

```python
from cacao_password_generator.core import generate
from cacao_password_generator.rating import rating
from cacao_password_generator.validate import validate

# Generate and validate
password = generate(length=16, minschars=3)

# Check if password meets requirements
is_valid, errors = validate(password, length=16, minschars=3)
print(f"Valid: {is_valid}")

# Get strength rating
strength_rating = rating(password)
print(f"Strength: {strength_rating}")  # e.g., "strong"
```

---

## ⚙️ Configuration

### Default Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `length` | 12 | Password length |
| `minlen` | 6 | Minimum allowed length |
| `maxlen` | 128 | Maximum allowed length |
| `minuchars` | 1 | Minimum uppercase letters |
| `minlchars` | 1 | Minimum lowercase letters |
| `minnumbers` | 1 | Minimum numbers |
| `minschars` | 1 | Minimum special characters |

### Environment Variables

Override defaults using environment variables with the `CACAO_PW_` prefix:

```bash
export CACAO_PW_MINLEN=8
export CACAO_PW_MAXLEN=32
export CACAO_PW_MINUCHARS=2
export CACAO_PW_MINLCHARS=4
export CACAO_PW_MINNUMBERS=3
export CACAO_PW_MINSCHARS=2

# Now cacao-pass uses these defaults
cacao-pass
```

### Character Sets

- **Uppercase**: A-Z (26 characters)
- **Lowercase**: a-z (26 characters)  
- **Numbers**: 0-9 (10 characters)
- **Special**: `!@#$%^&*()_+-=[]{}|;:,.<>?` (25 characters)

---

## 💡 Examples

### Web Application Passwords

```python
# Strong password for user accounts
user_password = generate(length=14, minuchars=2, minlchars=6, minnumbers=2, minschars=4)

# API key style (longer, more entropy)
api_key = generate(length=32, minuchars=4, minlchars=8, minnumbers=8, minschars=4)
```

### System Administration

```bash
# Database password (shell-safe considerations)
cacao-pass --length 20 --minschars 2

# SSH key passphrase
cacao-pass --length 25 --minuchars 3 --minlchars 8 --minnumbers 4
```

### Batch Generation

```python
from cacao_password_generator.core import generate

# Generate multiple passwords
passwords = [generate(length=16) for _ in range(10)]

# Generate with consistent strength
strong_passwords = [
    generate(length=18, minuchars=3, minlchars=6, minnumbers=3, minschars=6)
    for _ in range(5)
]
```

### Password Strength Analysis

```python
from cacao_password_generator.core import generate
from cacao_password_generator.rating import rating, detailed_rating

password = generate(length=20)
strength_rating = rating(password)
detailed_analysis = detailed_rating(password)

print(f"Password: {password}")
print(f"Strength: {strength_rating}")
print(f"Entropy: {detailed_analysis['entropy']:.2f} bits")
print(f"Character Space: {detailed_analysis['character_set_size']}")
print(f"Estimated Crack Time: {detailed_analysis['crack_time_formatted']}")
```

---

## 📋 Requirements

- **Python**: 3.8 or higher
- **Dependencies**: None (pure Python, uses only standard library)
- **Operating System**: Cross-platform (Windows, macOS, Linux)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Cacao Password Generator Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🙏 Acknowledgments

- Built with Python's `secrets` module for cryptographically secure random generation
- Inspired by the need for configurable, secure password generation in modern applications

---

**Made with 🍫 by the Cacao team**

*For more information, visit our [GitHub repository](https://github.com/cacao-research/cacao-password-generator) or [report issues](https://github.com/cacao-research/cacao-password-generator/issues).*