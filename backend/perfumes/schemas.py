from pydantic import BaseModel, Field
from typing import List
from uuid import UUID
from datetime import datetime

class Perfume(BaseModel):
    name : str = Field()
    brand : str = Field()
    price : float = Field()
    top_notes : List[str] = Field()
    heart_notes : List[str] = Field()
    base_notes : List[str] = Field()
    ingredients : List[str] | None = Field()
    description : List[str] | None = Field()


class PerfumeCreate(Perfume):
    ...

class PerfumeUpdate(Perfume):
    ...

class PerfumeDelete(Perfume):
    ...