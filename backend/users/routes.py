from auth.user_service import get_current_user
from users.schemas import User, UserResponse
from users.models import Users
from fastapi import APIRouter, Depends


users_router = APIRouter(prefix='/users', tags=['users'])

