import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import hash_secret_raw, Type

def derive_key(master_password: str, salt: bytes) -> bytes:
    return hash_secret_raw(
        secret=master_password.encode(),
        salt=salt,
        time_cost=2,         # Reduced from 5 to 2 for better performance
        memory_cost=65536,   # Reduced from 102400 to 65536 (64MB)
        parallelism=4,       # Reduced from 8 to 4
        hash_len=32,
        type=Type.ID
    )

def encrypt_password(plain_text: str, key: bytes) -> tuple:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    encrypted = aesgcm.encrypt(nonce, plain_text.encode(), None)
    return nonce, encrypted

def decrypt_password(encrypted_data: bytes, nonce: bytes, key: bytes) -> str:
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, encrypted_data, None).decode()
