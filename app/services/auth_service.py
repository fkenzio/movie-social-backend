from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, VerifyEmailRequest
from app.utils.security import get_password_hash, verify_password, create_access_token
from app.services.email_service import EmailService


class AuthService:

    @staticmethod
    def register(db: Session, user_data: RegisterRequest) -> User:
        # Verificar si el email ya existe
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )

        # Verificar si el username ya existe
        existing_username = db.query(User).filter(User.username == user_data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )

        # Generar código de verificación
        verification_code = EmailService.generate_verification_code()
        code_expires = datetime.utcnow() + timedelta(minutes=15)

        # Crear usuario
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            verification_code=verification_code,
            verification_code_expires=code_expires,
            is_verified=False
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Enviar email
        EmailService.send_verification_email(
            db_user.email,
            db_user.username,
            verification_code
        )

        return db_user

    @staticmethod
    def verify_email(db: Session, verify_data: VerifyEmailRequest) -> User:
        user = db.query(User).filter(User.email == verify_data.email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está verificado"
            )

        if user.verification_code != verify_data.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código de verificación inválido"
            )

        if datetime.utcnow() > user.verification_code_expires:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El código ha expirado"
            )

        user.is_verified = True
        user.verification_code = None
        user.verification_code_expires = None
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def login(db: Session, login_data: LoginRequest) -> dict:
        user = db.query(User).filter(User.email == login_data.email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )

        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )

        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Por favor verifica tu email primero"
            )

        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }

    @staticmethod
    def resend_code(db: Session, email: str) -> bool:
        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está verificado"
            )

        # Generar nuevo código
        verification_code = EmailService.generate_verification_code()
        user.verification_code = verification_code
        user.verification_code_expires = datetime.utcnow() + timedelta(minutes=15)

        db.commit()

        # Enviar email
        return EmailService.send_verification_email(
            user.email,
            user.username,
            verification_code
        )