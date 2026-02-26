import os
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

if __package__ is None or __package__ == '':
    from models import User
else:
    from .models import User

load_dotenv()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

ALGO = os.getenv("ALGORITHM", "HS256")
SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(32).hex())

def gen_hash(plain_passwd: str) -> str:
    return bcrypt_context.hash(plain_passwd)

# $2b$12$vMHP8LXWYKEZPQXTon.azuRoTbGC.WCQTaf21eE43ng39IBXNZf6y
def verify_password(plain_passwd: str, hashed_passwd: str) -> bool:
    return bcrypt_context.verify(plain_passwd, hashed_passwd)

def authenticate_user(username: str, password: str, *, db: Session, ) -> bool|User:
    user: Optional[User] = db.query(User).filter(User.username.ilike(username)).first() # case-insensitive. use username.lower()
    if not user:
        verify_password(password, "$2b$12$vMHP8LXWYKEZPQXTon.azuRoTbGC.WCQTaf21eE43ng39IBXNZf6y") # waste time to prevent timing attack
        time.sleep(0.1)
        return False
    if not verify_password(password, user.password_hash):
        time.sleep(0.1)
        return False
    return user


def create_access_token(username: str, *, user_id: int, user_role: str, expire_mins: int) -> str:
    to_encode = {
        "sub": username,
        "user_id": user_id,
        "role": user_role,
    }
    expires = datetime.now(timezone.utc) + timedelta(minutes=expire_mins)
    to_encode.update({"exp": int(expires.timestamp()),
                      "iat": int(datetime.now(timezone.utc).timestamp())})
    return jwt.encode(to_encode, algorithm=ALGO, key=SECRET_KEY)
