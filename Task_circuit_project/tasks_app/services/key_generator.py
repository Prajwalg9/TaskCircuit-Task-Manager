import random
import re
from tasks_app.models import UserProfile

WEAK_PATTERNS = [
    r'^0{6}$', r'^1{6}$', r'^2{6}$', r'^3{6}$', r'^4{6}$',
    r'^5{6}$', r'^6{6}$', r'^7{6}$', r'^8{6}$', r'^9{6}$',
    r'^123456$', r'^654321$', r'^012345$',
    r'^(\d)\1{5}$', r'^(\d{2})\1{2}$', r'^(\d{3})\1$',
]

def is_weak_pattern(key):
    for pattern in WEAK_PATTERNS:
        if re.match(pattern, key):
            return True
    return False

def is_key_available(key):
    return not UserProfile.objects.filter(unique_key=key).exists()

def validate_key(key):
    if len(key) != 6:
        return False, "Key must be exactly 6 digits"
    if not key.isdigit():
        return False, "Key must contain only numbers"
    if is_weak_pattern(key):
        return False, "Please choose a less predictable key"
    if not is_key_available(key):
        return False, "This key is already taken"
    return True, "Key is valid"

def generate_random_key():
    max_attempts = 100
    for _ in range(max_attempts):
        key = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        if not is_weak_pattern(key) and is_key_available(key):
            return key
    return None
