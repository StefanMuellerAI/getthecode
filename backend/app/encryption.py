"""Field-level encryption for sensitive database fields.

Uses AES-256-GCM for authenticated encryption with automatic IV generation.
Encrypted values are stored as base64-encoded strings with format:
    <iv>:<ciphertext>:<tag>

SECURITY:
- Each field gets a unique random IV (nonce)
- GCM mode provides authentication (detects tampering)
- Graceful fallback for unencrypted legacy data
"""
import base64
import os
import logging
from functools import lru_cache
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger(__name__)

# Encryption marker prefix to identify encrypted values
ENCRYPTION_PREFIX = "ENC:"


class EncryptionError(Exception):
    """Raised when encryption/decryption fails."""
    pass


@lru_cache()
def _get_encryption_key() -> Optional[bytes]:
    """Get the encryption key from settings.
    
    Returns None if encryption is disabled (no key configured).
    Cached to avoid repeated settings lookups.
    """
    from app.config import get_settings
    settings = get_settings()
    
    if not settings.encryption_key:
        return None
    
    try:
        key = base64.b64decode(settings.encryption_key)
        if len(key) != 32:
            raise ValueError(f"Encryption key must be 32 bytes, got {len(key)}")
        return key
    except Exception as e:
        logger.error(f"Invalid encryption key format: {e}")
        raise EncryptionError(f"Invalid encryption key: {e}")


def is_encryption_enabled() -> bool:
    """Check if encryption is enabled (key is configured)."""
    try:
        return _get_encryption_key() is not None
    except EncryptionError:
        return False


def _is_encrypted(value: str) -> bool:
    """Check if a value appears to be already encrypted."""
    return value.startswith(ENCRYPTION_PREFIX)


def encrypt_field(plaintext: Optional[str]) -> Optional[str]:
    """Encrypt a field value using AES-256-GCM.
    
    Args:
        plaintext: The value to encrypt. None values are passed through.
        
    Returns:
        Encrypted value as base64 string with format "ENC:<iv>:<ciphertext>:<tag>"
        Returns plaintext unchanged if encryption is disabled.
        
    Raises:
        EncryptionError: If encryption fails.
    """
    if plaintext is None:
        return None
    
    if not plaintext:
        return plaintext
    
    key = _get_encryption_key()
    if key is None:
        # Encryption disabled - return plaintext
        return plaintext
    
    # Don't double-encrypt
    if _is_encrypted(plaintext):
        return plaintext
    
    try:
        # Generate random 12-byte IV (recommended for GCM)
        iv = os.urandom(12)
        
        # Create AESGCM cipher
        aesgcm = AESGCM(key)
        
        # Encrypt (GCM combines ciphertext and tag)
        ciphertext = aesgcm.encrypt(iv, plaintext.encode('utf-8'), None)
        
        # Encode as base64 and combine with prefix
        iv_b64 = base64.b64encode(iv).decode('ascii')
        ct_b64 = base64.b64encode(ciphertext).decode('ascii')
        
        return f"{ENCRYPTION_PREFIX}{iv_b64}:{ct_b64}"
        
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise EncryptionError(f"Failed to encrypt field: {e}")


def decrypt_field(ciphertext: Optional[str]) -> Optional[str]:
    """Decrypt a field value using AES-256-GCM.
    
    Args:
        ciphertext: The encrypted value. None values are passed through.
        
    Returns:
        Decrypted plaintext string.
        Returns ciphertext unchanged if:
        - Encryption is disabled
        - Value doesn't appear to be encrypted (legacy data)
        
    Raises:
        EncryptionError: If decryption fails (invalid key, tampered data, etc.)
    """
    if ciphertext is None:
        return None
    
    if not ciphertext:
        return ciphertext
    
    # Check if value is encrypted
    if not _is_encrypted(ciphertext):
        # Legacy unencrypted data - return as-is
        return ciphertext
    
    key = _get_encryption_key()
    if key is None:
        # Encryption disabled but we have encrypted data
        # This is a configuration error - log warning and return as-is
        logger.warning("Found encrypted data but encryption key not configured")
        return ciphertext
    
    try:
        # Remove prefix and split
        encrypted_data = ciphertext[len(ENCRYPTION_PREFIX):]
        parts = encrypted_data.split(':')
        
        if len(parts) != 2:
            raise ValueError(f"Invalid encrypted format: expected 2 parts, got {len(parts)}")
        
        iv_b64, ct_b64 = parts
        
        # Decode from base64
        iv = base64.b64decode(iv_b64)
        ct = base64.b64decode(ct_b64)
        
        # Create AESGCM cipher and decrypt
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(iv, ct, None)
        
        return plaintext.decode('utf-8')
        
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise EncryptionError(f"Failed to decrypt field: {e}")


def generate_encryption_key() -> str:
    """Generate a new random 32-byte encryption key.
    
    Returns:
        Base64-encoded 32-byte key suitable for ENCRYPTION_KEY env var.
    """
    key = os.urandom(32)
    return base64.b64encode(key).decode('ascii')


# Convenience functions for batch operations

def encrypt_fields(data: dict, fields: list[str]) -> dict:
    """Encrypt multiple fields in a dictionary.
    
    Args:
        data: Dictionary containing fields to encrypt
        fields: List of field names to encrypt
        
    Returns:
        New dictionary with specified fields encrypted
    """
    result = data.copy()
    for field in fields:
        if field in result and result[field] is not None:
            result[field] = encrypt_field(result[field])
    return result


def decrypt_fields(data: dict, fields: list[str]) -> dict:
    """Decrypt multiple fields in a dictionary.
    
    Args:
        data: Dictionary containing fields to decrypt
        fields: List of field names to decrypt
        
    Returns:
        New dictionary with specified fields decrypted
    """
    result = data.copy()
    for field in fields:
        if field in result and result[field] is not None:
            result[field] = decrypt_field(result[field])
    return result

