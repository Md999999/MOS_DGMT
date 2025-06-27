from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.utils import success_response,error_response
from app.storage import InMemoryStorage

router = APIRouter()

SECRET_KEY = "mysecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context= CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_token(username: str):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/register")
def register(form: OAuth2PasswordRequestForm = Depends()):
    if form.username in InMemoryStorage.users:
        raise HTTPException(status_code=400, detail=error_response("User exists"))
    InMemoryStorage.users[form.username] = hash_password(form.password)
    return success_response("User registered") 

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = InMemoryStorage.users.get(form.username)
    if not user or  not verify_password(form.password, user):
        raise HTTPException(status_code=400, detail=error_response("Wrong credentials"))
    token = create_token(form.username)
    return success_response("Login Ssccessful",{"access_token": token, "token_type": "bearer"})

@router.get("/protected")
def protected(user: str = Depends(get_current_user)):
    return success_response("Authenticated",{"user": user})
