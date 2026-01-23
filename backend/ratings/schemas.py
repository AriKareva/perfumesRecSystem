from typing import Optional
from pydantic import BaseModel, Field


class Rating(BaseModel):
    user_id : int = Field(...)
    perfume_id : int = Field(...)
    rate : int = Field(...)
    comment : Optional[str] = Field(min_length=3)


class RatingCreate(Rating):
    ...


class RatingUpdate(Rating):
    ...


class RatingResponse(Rating):
    ...
    

class RatingDelete(Rating):
    ...

class RatingExistsException(BaseException):
    message: str = 'Парфюм уже оценен :('