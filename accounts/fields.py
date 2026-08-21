import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken

from django.conf import settings
from django.db import models


def get_fernet_cipher() -> Fernet:
    key = getattr(settings, 'FIELD_ENCRYPTION_KEY', None)
    if not key:
        secret = getattr(settings, 'SECRET_KEY', 'default-django-secret-key-fallback')
        digest = hashlib.sha256(secret.encode('utf-8')).digest()
        key = base64.urlsafe_b64encode(digest)
    elif isinstance(key, str):
        key = key.encode('utf-8')
    return Fernet(key)


class EncryptedCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        # Fernet ciphertext is longer than the plaintext (around 100+ chars for short strings)
        kwargs.setdefault('max_length', 255)
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None or value == '':
            return value
        try:
            cipher = get_fernet_cipher()
            return cipher.decrypt(value.encode('utf-8')).decode('utf-8')
        except (InvalidToken, Exception):
            # Fallback to raw value if already plaintext or unable to decrypt
            return value

    def to_python(self, value):
        if isinstance(value, str) or value is None:
            return value
        return str(value)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None or value == '':
            return value
        
        cipher = get_fernet_cipher()
        # Avoid double encryption if value is already encrypted with current key
        try:
            cipher.decrypt(value.encode('utf-8'))
            return value
        except Exception:
            pass

        return cipher.encrypt(value.encode('utf-8')).decode('utf-8')

