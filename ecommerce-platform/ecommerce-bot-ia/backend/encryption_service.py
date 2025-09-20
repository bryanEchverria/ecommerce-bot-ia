import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class EncryptionService:
    """Servicio para encriptar/desencriptar tokens sensibles"""
    
    def __init__(self):
        self._key = None
        self._fernet = None
        self._initialize_key()
    
    def _initialize_key(self):
        """Inicializa la clave de encriptación"""
        try:
            # Obtener la clave secreta del entorno
            secret_key = os.getenv("SECRET_KEY", "fallback-secret-key-change-in-production")
            
            # Generar clave de encriptación usando PBKDF2
            password = secret_key.encode()
            salt = b'salt_for_whatsapp_tokens'  # En producción, usar salt único por instalación
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password))
            self._fernet = Fernet(key)
            
        except Exception as e:
            logger.error(f"Error initializing encryption service: {str(e)}")
            raise
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encripta un texto plano
        
        Args:
            plaintext: Texto a encriptar
            
        Returns:
            str: Texto encriptado en base64
        """
        if not plaintext:
            return ""
        
        try:
            encrypted_bytes = self._fernet.encrypt(plaintext.encode())
            return base64.urlsafe_b64encode(encrypted_bytes).decode()
        except Exception as e:
            logger.error(f"Error encrypting text: {str(e)}")
            raise
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        Desencripta un texto encriptado
        
        Args:
            encrypted_text: Texto encriptado en base64
            
        Returns:
            str: Texto plano desencriptado
        """
        if not encrypted_text:
            return ""
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode())
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Error decrypting text: {str(e)}")
            raise
    
    def is_encrypted(self, text: str) -> bool:
        """
        Verifica si un texto está encriptado
        
        Args:
            text: Texto a verificar
            
        Returns:
            bool: True si parece estar encriptado
        """
        if not text:
            return False
        
        try:
            # Intenta decodificar base64 y desencriptar
            self.decrypt(text)
            return True
        except:
            return False

# Instancia global del servicio de encriptación
encryption_service = EncryptionService()

def encrypt_sensitive_data(data: str) -> str:
    """Función de conveniencia para encriptar datos sensibles"""
    return encryption_service.encrypt(data)

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Función de conveniencia para desencriptar datos sensibles"""
    return encryption_service.decrypt(encrypted_data)