from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from typing import Optional
from config import settings

def create_access_token(user_id: int, nickname: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "sub": str(user_id),
        "nickname": nickname,
        "exp": expire
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        nickname = payload.get("nickname")
        if user_id is None or nickname is None:
            return None
        return {"id": int(user_id), "nickname": nickname}
    except JWTError:
        return None
