from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import hashlib
from app.config import settings

# Configuración de bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña"""
    # Pre-hashear con SHA256 para evitar límite de bcrypt
    password_sha256 = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    return pwd_context.verify(password_sha256, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hashear contraseña usando SHA256 primero para evitar límite de bcrypt
    bcrypt tiene límite de 72 bytes, así que pre-hasheamos con SHA256
    """
    # Pre-hashear con SHA256 para evitar el límite de 72 bytes de bcrypt
    password_sha256 = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return pwd_context.hash(password_sha256)


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