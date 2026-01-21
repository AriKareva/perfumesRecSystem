# backend/app/security/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.security.jwt_handler import decode_access_token

security = HTTPBearer()

async def get_current_user(credentials = Depends(security)) -> dict:
    token = credentials.credentials
    user = decode_access_token(token)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или истёкший токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
