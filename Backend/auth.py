from datetime import datetime, timedelta
import os
from jose import JWTError, jwt

from passlib.context import CryptContext

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# =========================
# CONFIG
# =========================
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")

REFRESH_EXPIRE_DAYS = 7



ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 1

security = HTTPBearer()
# =========================
# PASSWORD HASHING
# =========================
pwd_context = CryptContext(
    schemes=["argon2"]
)
def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(
    plain_password,
    hashed_password
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# =========================
# JWT TOKEN
# =========================

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def create_refresh_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS)

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        REFRESH_SECRET_KEY,
        algorithm="HS256"
    )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("user_id")
        email = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return {
            "user_id": user_id,
            "email": email
        }

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token is invalid or expired"
        )