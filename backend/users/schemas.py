from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class User(BaseModel):
    nickname : str = Field(...)

class UserCreate(User):
    email : EmailStr = Field(...)
    password : str = Field(...)
    password_2 : str = Field(...)

class UserUpdate(User):
    ...

class UserResponse(User):
    email : EmailStr = Field(...)
    model_config = ConfigDict(
        from_attributes=True
    )

class UserDelete(User):
    ...

class UserLogin(User):
    password : str = Field(...)



class TokenResponse(BaseModel):
    access_token : str = Field(...)
    token_type : str = Field(...)