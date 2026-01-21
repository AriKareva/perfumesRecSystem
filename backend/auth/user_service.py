from http.server import HTTPServer
from auth.security.password_hasher import hash_password, verify_password
from auth.security.jwt_handler import decode_access_token
from users.schemas import UserCreate
from users.models import Users
from sqlalchemy.orm import Session
from db.connection import get_db
from fastapi import HTTPException, status
from fastapi import Depends



def confirm_password(password1 :str , password2 : str):
    if password1 != password2:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пароли не совпадают"
        )
    
def check_email_not_exists(email : str, db : Session = Depends(get_db)):
    user_with_email = db.query(Users).filter(Users.email == email).all()
    if user_with_email:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
    
security = HTTPServer()

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


class UserService:
    @staticmethod
    def register(user_data : UserCreate, db : Session = Depends(get_db)):
        confirm_password(user_data.password, user_data.password)
        check_email_not_exists(user_data.email, db)

        new_user = Users(
            nickname = user_data.nickname,
            email = user_data.email,
            password_enc = hash_password(user_data.password)
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user
    
    def verify_creditals(user_data : int, db : Session = Depends(get_db)):
        user = db.query(Users).filter(Users.nickname == user_data.nickname).first()
        if not user or not verify_password(user_data.password, user.password_enc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
        return user
        
