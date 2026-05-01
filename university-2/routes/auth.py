from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from controllers.auth_controller import AuthController
from database import get_db
from models.auth_model import OTPRequest, OTPVerifyRequest, MessageResponse, AuthTokenResponse


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/request-otp", response_model=MessageResponse)
def request_otp(payload: OTPRequest, db: Session = Depends(get_db)):
    AuthController.request_otp(payload.email, db)
    return {"message": "Si el correo es valido, el OTP fue enviado"}


@router.post("/verify-otp", response_model=AuthTokenResponse)
def verify_otp(payload: OTPVerifyRequest, db: Session = Depends(get_db)):
    return AuthController.verify_otp(payload.email, payload.code, db)
