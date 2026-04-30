import os
import re
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from models.db_model import OTPCode, AuthSession


OTP_TTL_MINUTES = 10
SESSION_TTL_HOURS = 12

security = HTTPBearer(auto_error=False)


class AuthController:
    @staticmethod
    def _validate_email(email: str) -> str:
        normalized = email.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", normalized):
            raise HTTPException(status_code=400, detail="Correo invalido")
        return normalized

    @staticmethod
    def _send_otp_email(email: str, code: str) -> None:
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        smtp_from = os.getenv("SMTP_FROM", smtp_user or "no-reply@example.com")

        if not smtp_user or not smtp_password:
            print(f"[OTP DEV] Codigo para {email}: {code}")
            return

        msg = EmailMessage()
        msg["Subject"] = "Codigo OTP - University"
        msg["From"] = smtp_from
        msg["To"] = email
        msg.set_content(
            f"Tu codigo OTP es: {code}\n\n"
            f"Este codigo expira en {OTP_TTL_MINUTES} minutos."
        )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

    @staticmethod
    def request_otp(email: str, db: Session = Depends(get_db)) -> None:
        normalized_email = AuthController._validate_email(email)
        code = f"{secrets.randbelow(1000000):06d}"
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_TTL_MINUTES)

        db.query(OTPCode).filter(
            OTPCode.email == normalized_email,
            OTPCode.used.is_(False)
        ).update({"used": True})

        db_code = OTPCode(
            email=normalized_email,
            code=code,
            expires_at=expires_at,
            used=False,
        )
        db.add(db_code)
        db.commit()

        AuthController._send_otp_email(normalized_email, code)

    @staticmethod
    def verify_otp(email: str, code: str, db: Session = Depends(get_db)) -> dict:
        normalized_email = AuthController._validate_email(email)
        now = datetime.now(timezone.utc)

        otp_row = (
            db.query(OTPCode)
            .filter(
                OTPCode.email == normalized_email,
                OTPCode.code == code,
                OTPCode.used.is_(False),
            )
            .order_by(OTPCode.created_at.desc())
            .first()
        )

        if not otp_row:
            raise HTTPException(status_code=401, detail="Codigo OTP invalido")

        expires_at = otp_row.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < now:
            otp_row.used = True
            db.commit()
            raise HTTPException(status_code=401, detail="Codigo OTP expirado")

        otp_row.used = True

        token = secrets.token_urlsafe(32)
        session_expires_at = now + timedelta(hours=SESSION_TTL_HOURS)

        db_session = AuthSession(
            email=normalized_email,
            token=token,
            expires_at=session_expires_at,
        )
        db.add(db_session)
        db.commit()

        return {
            "token": token,
            "token_type": "bearer",
            "expires_in_seconds": SESSION_TTL_HOURS * 3600,
        }

    @staticmethod
    def require_auth(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db),
    ) -> AuthSession:
        if not credentials or credentials.scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No autorizado",
            )

        session = db.query(AuthSession).filter(AuthSession.token == credentials.credentials).first()
        if not session:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")

        expires_at = session.expires_at
        now = datetime.now(timezone.utc)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < now:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")

        return session