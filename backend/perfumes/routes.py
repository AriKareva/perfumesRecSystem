from ratings.models import Ratings
from perfumes.models import Brands, PerfumeNotes, Perfumes
from db.connection import get_db
from perfumes.schemas import PerfumeCreate, PerfumeUpdate, PerfumeResponse, PerfumeDelete
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from sqlalchemy.sql.expression import or_
from typing import List, Optional, Union


perfumes_router = APIRouter(prefix='/perfumes', tags=['perfumes'])

@perfumes_router.get('/', response_model=List[PerfumeResponse])
async def get_all_perfumes(db: Session = Depends(get_db)):
    perfumes = db.query(Perfumes)\
        .options(
            joinedload(Perfumes.brand),
            joinedload(Perfumes.concentration),
            joinedload(Perfumes.rating),
            joinedload(Perfumes.perfume_note) 
        )\
        .all()

    return perfumes

@perfumes_router.get('/5rand_perfumes', response_model=Union[List[PerfumeResponse], dict])
async def get_5_rand_perfumes(user_id : int, perfumes_to_rate_n : int = 5, db: Session = Depends(get_db)):
    # смотрим оцененные парфюмы пользователя:
    rated_ids = db.query(Ratings).with_entities(Ratings.perfume_id).filter(Ratings.user_id == user_id).subquery()

    rated_cnt =db.query(Ratings).filter(Ratings.user_id == user_id).count()
    perfumes_cnt = db.query(Perfumes).count()

    # если пользователь уже оценил все парфюмы в системе
    if rated_cnt == perfumes_cnt:

        if perfumes_cnt == 0:
            return {'message' : 'Нет парфюмов для оценки :('}

        return {'message' : 'Все парфюмы уже оценены :('}
    
    rand_perfumes = db.query(Perfumes).filter(~Perfumes.id.in_(rated_ids)).order_by(func.random()).limit(perfumes_to_rate_n)

    return rand_perfumes

# @perfumes_router.get('/{name}', response_model=PerfumeResponse)
# async def get_perfume_by_name(name : str, db : Session = Depends(get_db)):
#     perfume = db.query(Perfumes).filter(Perfumes.name == name).all()

#     return perfume

# @perfumes_router.get('/search', response_model=dict)
# async def serch_perfumes(db: Session = Depends(get_db)):
#     return {'message' : 'аааааааааааааааааааааааааааааааа :('}
