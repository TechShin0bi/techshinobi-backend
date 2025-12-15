import secrets
import string

def generate_unsubscribe_token():
    """Generate a secure random token for unsubscribing."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))
