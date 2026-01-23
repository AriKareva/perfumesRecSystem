from auth.security.jwt_handler import create_access_token
from auth.user_service import UserService
from db.connection import get_db
from users.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


auth_router = APIRouter(prefix='/auth', tags=['auth'])


@auth_router.post('/register', response_model=UserResponse)
async def register_user(user_data : UserCreate, db : Session = Depends(get_db)):
    new_user = UserService.register(user_data, db)
    return new_user

@auth_router.post('/login', response_model=TokenResponse)
async def login_user(user_data : UserLogin, db: Session = Depends(get_db)):
    user = UserService.verify_creditals(user_data, db)
    access_token = create_access_token(user.id, user.nickname)
    return {"access_token": access_token, "token_type": "Bearer"}
