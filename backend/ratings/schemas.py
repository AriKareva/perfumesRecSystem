from typing import Optional
from Pydantic import BaseModel, Field


class Rating(BaseModel):
    user = ...
    perfume = ...
    rate : Optional[int] = Field()
    comment : Optional[str] = Field(min_length=3)


class RatingCreate(Rating):
    ...


class RatingUpdate(Rating):
    ...


class RatingResponse(Rating):
    ...
    

class RatingDelete(Rating):
    ...