from datetime import datetime, timedelta, timezone
from sendmail import send_email
from fastapi import APIRouter, Depends, HTTPException, status,Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import secrets
from database import get_db
from models import EmailOtp, User
from security import create_token, decode_token, hash_password, verify_password
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(tags=["auth"])
bearer_scheme = HTTPBearer()


class RegisterInput(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)  # bcrypt ignores bytes past 72
    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v

class verifyotp(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)  # bcrypt ignores bytes past 72
    otp: str = Field(pattern=r"^[0-9]{6}$")
    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v

class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class UserOut(BaseModel):
    id: int
    name: str
    email: str


class AuthOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


def _auth_response(user: User) -> AuthOut:
    return AuthOut(
        access_token=create_token(user.id),
        user=UserOut(id=user.id, name=user.name, email=user.email),
    )




def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    user_id = decode_token(creds.credentials)
    user = db.get(User, user_id) if user_id is not None else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return user

def generate_otp():
    return str(secrets.randbelow(1000000)).zfill(6)

@router.post("/register")
@limiter.limit("3/minute")
def register(data: RegisterInput,Request: Request, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    db.query(EmailOtp).filter(EmailOtp.email == email, EmailOtp.used == False).delete()
    otp = generate_otp()
    otp_record = EmailOtp(email=email, otp=otp, expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),used=False,attempts=00)
                          
    db.add(otp_record)
    db.commit()
    try:
        send_email(email, otp)  # Implement this function to send the OTP via email
    except Exception as e:
        db.delete(otp_record)
        db.commit()
        raise HTTPException(status_code=500, detail="Failed to send OTP")
    return {"message": "OTP sent successfully. Please verify your email using the OTP."}


@router.post("/verify-otp",response_model=AuthOut,status_code=status.HTTP_201_CREATED)
def verify_otp(data: verifyotp, db: Session = Depends(get_db)):
    email = data.email.lower()
    otp_record = (
        db.query(EmailOtp).filter(EmailOtp.email == email,EmailOtp.used.is_(False),).first())
    if not otp_record:
        raise HTTPException(status_code=400, detail="otp not found or already used, request a new one")
    expires_at = otp_record.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at <= datetime.now(timezone.utc):
        db.delete(otp_record)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="OTP has expired. Request a new one.",
        )
    if otp_record.attempts >= 5:
        raise HTTPException(status_code=400, detail="Maximum OTP verification attempts exceeded")
    
    if otp_record.otp != data.otp:
        otp_record.attempts += 1
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid OTP")
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(name=data.name, email=email, password_hash=hash_password(data.password))
    db.add(user)
    db.delete(otp_record)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    
    
    db.refresh(user)
    return _auth_response(user)


@router.post("/login", response_model=AuthOut)
def login(data: LoginInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return _auth_response(user)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return UserOut(id=current_user.id, name=current_user.name, email=current_user.email)
