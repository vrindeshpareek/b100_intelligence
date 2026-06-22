import base64
import hashlib
import secrets

import bcrypt
from cryptography.fernet import Fernet
from django.conf import settings


def _fernet():
    key = base64.urlsafe_b64encode(
        hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    )
    return Fernet(key)


def create_secret():
    plain = secrets.token_urlsafe(32)
    return (
        plain,
        bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode(),
        _fernet().encrypt(plain.encode()).decode(),
    )


def decrypt_secret(encrypted):
    return _fernet().decrypt(encrypted.encode()).decode()
