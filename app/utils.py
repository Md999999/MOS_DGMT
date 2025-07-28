import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta
import hashlib

load_dotenv()

# Email sending function
def send_email(to_email: str, subject: str, body: str):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USERNAME")
    smtp_pass = os.getenv("SMTP_PASSWORD")

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email send failed: {e}")

# Password hashing and verification using SHA256 (or switch to bcrypt if you want)
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str):
    return hash_password(plain_password) == hashed_password


JWT_SECRET = os.getenv("JWT_SECRET", "defaultsecret")
JWT_ALGORITHM = "HS256"

def create_jwt_token(data: dict, expires: int = 1800):  # expires in seconds, default 30 min
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(seconds=expires)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")

def success_response(message: str, data=None):
    return {"status": True, "message": message, "data": data}

def error_response(message: str):
    return {"status": False, "message": message}
