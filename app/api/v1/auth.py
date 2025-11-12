from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    VerifyEmailRequest,
    ResendCodeRequest,
    Token
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(user_data: RegisterRequest, db: Session = Depends(get_db)):
    """Registrar nuevo usuario"""
    user = AuthService.register(db, user_data)
    return user


@router.post("/verify-email", response_model=Token)
def verify_email(verify_data: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Verificar email con código"""
    user = AuthService.verify_email(db, verify_data)

    # Generar token después de verificar
    from app.utils.security import create_access_token
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Iniciar sesión"""
    return AuthService.login(db, login_data)


@router.post("/resend-code")
def resend_code(data: ResendCodeRequest, db: Session = Depends(get_db)):
    """Reenviar código de verificación"""
    success = AuthService.resend_code(db, data.email)
    if success:
        return {"message": "Código reenviado exitosamente"}
    raise HTTPException(status_code=500, detail="Error al enviar el código")