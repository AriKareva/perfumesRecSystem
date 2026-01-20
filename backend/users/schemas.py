from datetime import datetime
from typing import Optional
from Pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    nickname : str = Field()
    email : EmailStr = Field()

class UserCreate(User):
    ...

class UserUpdate(User):
    ...

class UserResponse(User):
    ...


class UserDelete(User):
    ...


def validate_username(username):
    ...

def validate_password(password):
    ...

def confirm_password(password1, password2):
    ...