import random
import string

def generate_short_id(length: int = 4) -> str:
    """Generate a short alphanumeric ID."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length)) 