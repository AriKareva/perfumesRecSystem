from auth.user_service import get_current_user
from users.models import Users
from ratings.schemas import RatingCreate, RatingExistsException, RatingResponse
from db.connection import get_db
from ratings.models import Ratings
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

ratings_router = APIRouter(prefix='/ratings', tags=['ratings'])

@ratings_router.post('/rate/{perfume_id}', response_model=RatingResponse)
async def rate_perfume(
    perfume_id: int, 
    rate: int, 
    db: Session = Depends(get_db), 
    current_user: Users = Depends(get_current_user) 
):

    rating_exists = db.query(Ratings).filter(
        Ratings.user_id == current_user.id,
        Ratings.perfume_id == perfume_id 
    ).first()
    
    if rating_exists:
        raise RatingExistsException()

    new_rating = Ratings(
        rate=rate,
        user_id=current_user.id,
        perfume_id=perfume_id 
    )
    
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating