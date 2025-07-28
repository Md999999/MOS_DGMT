from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.utils import (
    create_jwt_token,
    decode_jwt_token,
    hash_password,
    verify_password,
    send_email,
    success_response,
    error_response,
)
from app.database import get_db
from app.models import User
from jose import JWTError
from datetime import datetime, timedelta

router = APIRouter()

SECRET_KEY = "mysecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_jwt_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/register")
def register(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if user:
        raise HTTPException(status_code=400, detail=error_response("User exists"))

    hashed_pw = hash_password(form.password)
    new_user = User(username=form.username, hashed_password=hashed_pw, email_verified=False)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_jwt_token({"sub": new_user.username}, expires=1800)
    verify_link = f"http://localhost:8000/verify-email?token={token}"

    send_email(new_user.username, "Verify your email", f"<a href='{verify_link}'>Click to verify</a>")

    return success_response("User registered")

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail=error_response("Wrong credentials"))
    token = create_jwt_token({"sub": user.username})
    return success_response("Login Successful", {"access_token": token, "token_type": "bearer"})

@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    payload = decode_jwt_token(token)
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="No user with that email")
    user.email_verified = True
    db.commit()
    return success_response("Email verified successfully")

@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    payload = decode_jwt_token(token)
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = hash_password(new_password)
    db.commit()
    return success_response("Password reset successful")
