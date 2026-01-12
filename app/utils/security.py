from datetime import datetime, timedelta
from typing import Optional
import hashlib
import base64
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# Configuración de bcrypt con backend específico
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__default_rounds=12,
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña con pre-hash SHA256"""
    # Pre-hash con SHA256 para evitar límite de 72 bytes
    password_hash = hashlib.sha256(plain_password.encode('utf-8')).digest()
    password_b64 = base64.b64encode(password_hash).decode('utf-8')
    return pwd_context.verify(password_b64, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hashear contraseña con pre-hash SHA256 para evitar límite de bcrypt
    """
    # Pre-hash con SHA256 (siempre produce 32 bytes)
    password_hash = hashlib.sha256(password.encode('utf-8')).digest()
    # Encode en base64 (produce ~44 caracteres, bien bajo el límite de 72)
    password_b64 = base64.b64encode(password_hash).decode('utf-8')
    return pwd_context.hash(password_b64)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crear token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decodificar token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None