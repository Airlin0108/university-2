from pydantic import BaseModel, Field


class OTPRequest(BaseModel):
    email: str


class OTPVerifyRequest(BaseModel):
    email: str
    code: str = Field(..., min_length=6, max_length=6)


class MessageResponse(BaseModel):
    message: str


class AuthTokenResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    expires_in_seconds: int
