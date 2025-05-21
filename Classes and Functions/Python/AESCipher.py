"""
`pip install cryptography`

"""

from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64

class AESCipher:
    def __init__(self, key: bytes, salt: bytes, iterations: int = 100_000):
        """
        Initialize the cipher with a password-based key derivation using SHA256.
        :param key: The user-provided key (e.g., a password or secret).
        :param salt: A salt for KDF (must be securely generated and saved).
        :param iterations: Number of iterations for key derivation.
        """
        self.backend = default_backend()
        self.key = self._derive_key(key, salt, iterations)

    def _derive_key(self, password: bytes, salt: bytes, iterations: int) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # AES-256 requires a 32-byte key
            salt=salt,
            iterations=iterations,
            backend=self.backend
        )
        return kdf.derive(password)

    def encrypt(self, plaintext: bytes) -> bytes:
        iv = os.urandom(16)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()

        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        return base64.b64encode(iv + ciphertext)

    def decrypt(self, encrypted_data: bytes) -> bytes:
        try:
            raw = base64.b64decode(encrypted_data)
            if len(raw) < 16:
                raise ValueError("Invalid encrypted data: too short for IV")

            iv = raw[:16]
            ciphertext = raw[16:]

            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
            return plaintext

        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

# Example usage
if __name__ == "__main__":
    key = b'08180230818209389012832132109123'
    salt = os.urandom(16)

    aes = AESCipher(key, salt)

    data = b'This is very secret data!'
    encrypted = aes.encrypt(data)
    print("Encrypted:", encrypted)

    decrypted = aes.decrypt(encrypted)
    print("Decrypted:", decrypted)

