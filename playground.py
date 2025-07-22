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

print(password) 

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