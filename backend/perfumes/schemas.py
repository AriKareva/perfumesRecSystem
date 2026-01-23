from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from uuid import UUID
from datetime import datetime

# концентрация
class Concentration(BaseModel):
    id: int = Field()
    concentration_title : str = Field(min_length=2)
    # concentration_code: str = Field()

class ConcentrationCreate(Concentration):
    ...

class ConcentrationUpdate(Concentration):
    ...

class ConcentrationResponse(Concentration):
    model_config = ConfigDict(
        from_attributes = True
    )

class ConcentrationDelete(Concentration):
    ...


# бренды
class Brand(BaseModel):
    id : int = Field()
    name : str = Field(min_length=2)

class BrandCreate(Brand):
    ...

class BrandUpdate(Brand):
    ...

class BrandResponse(Brand):
    model_config = ConfigDict(
        from_attributes=True 
    )

class BrandDelete(Brand):
    ...


# ноты
class Note(BaseModel):
    id : int = Field(...)
    note_name : Optional[str] = None

class NoteCreate(Note):
    ...

class NoteUpdate(Note):
    ...

class NoteResponse(Note):
    model_config = ConfigDict(
        from_attributes=True 
    )

class NoteDelete(Note):
    ...


# типы нот
class NoteType(BaseModel):
    id : int = Field(...)
    note_type_name : Optional[str] = None

class NoteTypeCreate(NoteType):
    ...

class NoteTypeUpdate(NoteType):
    ...

class NoteTypesResponse(NoteType):
    model_config = ConfigDict(
        from_attributes=True 
    )

class NoteTypesDelete(NoteType):
    ...


# парфюмы
class Perfume(BaseModel):
    id : int = Field(...)
    name : str = Field(min_length=2)
    brand : Optional[Brand] = None
    price : Optional[float] = None
    photo : Optional[str] = None
    concentration : Optional[Concentration] = None
    description : Optional[str] = None

class PerfumeCreate(Perfume):
    ...

class PerfumeUpdate(Perfume):
    ...

class PerfumeResponse(Perfume):
    model_config = ConfigDict(
        from_attributes=True 
    )

class PerfumeDelete(Perfume):
    ...



class MessageResponse(BaseModel):
    message : str = Field(...)