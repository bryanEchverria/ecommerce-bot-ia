"""
Utilidades de cifrado para datos sensibles multi-tenant
"""
from cryptography.fernet import Fernet
import base64
import hashlib
import os
import logging

logger = logging.getLogger(__name__)

def _fernet():
    """
    Deriva una clave de 32 bytes desde SECRET_KEY para Fernet
    """
    secret = os.environ.get("SECRET_KEY", "change-me")
    key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest())
    return Fernet(key)

def encrypt_token(token: str) -> bytes:
    """
    Cifra un token de autenticación
    
    Args:
        token: Token en texto plano
        
    Returns:
        Token cifrado como bytes
    """
    try:
        return _fernet().encrypt(token.encode())
    except Exception as e:
        logger.error(f"Error encrypting token: {e}")
        raise

def decrypt_token(encrypted_token: bytes) -> str:
    """
    Descifra un token de autenticación
    
    Args:
        encrypted_token: Token cifrado como bytes
        
    Returns:
        Token en texto plano
    """
    try:
        return _fernet().decrypt(encrypted_token).decode()
    except Exception as e:
        logger.error(f"Error decrypting token: {e}")
        raise