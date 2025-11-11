import hashlib
import hmac
from datetime import datetime

def generate_signature(secret: str, message: str) -> str:
    """
    Generate HMAC signature for webhook verification
    """
    return hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def verify_signature(secret: str, message: str, signature: str) -> bool:
    """
    Verify HMAC signature for webhook requests
    """
    expected_signature = generate_signature(secret, message)
    return hmac.compare_digest(expected_signature, signature)