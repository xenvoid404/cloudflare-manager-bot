import base64
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional

from config import config

logger = logging.getLogger(__name__)

class Encryption:
    """Utility class for encrypting and decrypting sensitive data."""
    
    def __init__(self):
        self._fernet: Optional[Fernet] = None
        self._initialize_encryption()
    
    def _initialize_encryption(self) -> None:
        """Initialize the encryption cipher."""
        if not config.ENCRYPTION_KEY:
            logger.warning("No encryption key provided. Encryption will be disabled.")
            return
        
        try:
            # Use PBKDF2 to derive a proper key from the provided key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'stable_salt_for_bot',  # In production, use a random salt per installation
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(config.ENCRYPTION_KEY.encode()))
            self._fernet = Fernet(key)
            logger.info("Encryption initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            self._fernet = None
    
    def encrypt(self, data: str) -> str:
        """Encrypt a string and return base64 encoded result."""
        if not self._fernet:
            logger.warning("Encryption not available, returning plain text")
            return data
        
        try:
            encrypted_data = self._fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return data
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt a base64 encoded encrypted string."""
        if not self._fernet:
            logger.warning("Encryption not available, returning data as-is")
            return encrypted_data
        
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self._fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return encrypted_data
    
    def is_available(self) -> bool:
        """Check if encryption is available."""
        return self._fernet is not None

# Global encryption instance
encryption = Encryption()