"""
Encryption utilities for PII protection.
Uses Fernet symmetric encryption for secure storage of sensitive data.
"""

import os
import base64
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken


_fernet_instance: Optional[Fernet] = None


def get_encryption_key() -> bytes:
    """
    Get the encryption key from environment variable.
    Generates a new key if not set (for development only).
    """
    key = os.getenv("PII_ENCRYPTION_KEY")
    
    if not key:
        # For development/demo: generate a key and warn
        print("WARNING: PII_ENCRYPTION_KEY not set. Generating temporary key.")
        print("For production, set PII_ENCRYPTION_KEY environment variable.")
        key = Fernet.generate_key().decode()
        os.environ["PII_ENCRYPTION_KEY"] = key
    
    return key.encode() if isinstance(key, str) else key


def get_fernet() -> Fernet:
    """Get or create Fernet instance for encryption/decryption."""
    global _fernet_instance
    if _fernet_instance is None:
        _fernet_instance = Fernet(get_encryption_key())
    return _fernet_instance


def encrypt_value(value: str) -> bytes:
    """
    Encrypt a string value using Fernet symmetric encryption.
    
    Args:
        value: The plaintext string to encrypt
        
    Returns:
        Encrypted bytes
    """
    if not value:
        return b''
    
    fernet = get_fernet()
    return fernet.encrypt(value.encode('utf-8'))


def decrypt_value(encrypted_value: bytes) -> str:
    """
    Decrypt an encrypted value back to plaintext.
    
    Args:
        encrypted_value: The encrypted bytes
        
    Returns:
        Decrypted plaintext string
        
    Raises:
        InvalidToken: If decryption fails (wrong key or corrupted data)
    """
    if not encrypted_value:
        return ''
    
    fernet = get_fernet()
    try:
        return fernet.decrypt(encrypted_value).decode('utf-8')
    except InvalidToken:
        raise ValueError("Failed to decrypt value. Invalid key or corrupted data.")


def generate_new_key() -> str:
    """
    Generate a new Fernet encryption key.
    Use this for initial setup or key rotation.
    
    Returns:
        Base64-encoded key string suitable for environment variable
    """
    return Fernet.generate_key().decode()


def reset_fernet():
    """Reset the cached Fernet instance. Used for testing or key rotation."""
    global _fernet_instance
    _fernet_instance = None
