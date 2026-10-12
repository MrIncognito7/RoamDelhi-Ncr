from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import User
from security import create_token, decode_token, hash_password, verify_password

router = APIRouter(tags=["auth"])
bearer_scheme = HTTPBearer()


# ---------- request / response shapes ----------

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


# ---------- dependency: use on any route that needs a logged-in user ----------

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


# ---------- endpoints ----------

@router.post("/register", response_model=AuthOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterInput, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(name=data.name, email=email, password_hash=hash_password(data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:  # two simultaneous sign-ups with the same email
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    db.refresh(user)
    return _auth_response(user)


@router.post("/login", response_model=AuthOut)
def login(data: LoginInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    # Same message for "no such email" and "wrong password" so emails can't be probed.
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return _auth_response(user)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return UserOut(id=current_user.id, name=current_user.name, email=current_user.email)
