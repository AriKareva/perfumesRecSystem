import datetime
from typing import Any, Dict, List, Optional
from backend.perfumes.schemas import Perfume
from ratings.models import Ratings
from users.models import Users
from sqlalchemy import Session
from sqlalchemy import func


class UserDAO:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_by_id(self, user_id: int) -> Optional[Users]:
        return self.db.query(Users).filter(Users.id == user_id).first()
    
    def get_all_active(self, limit: int = 1000) -> List[Users]:
        return self.db.query(Users)\
            .order_by(Users.created_at.desc())\
            .limit(limit)\
            .all()
    
    def update_last_active(self, user_id: int):
        user = self.get_by_id(user_id)
        if user and hasattr(user, 'last_active'):
            user.last_active = datetime.now()
            self.db.commit()
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        stats = self.db.query(
            func.count(Ratings.id).label('total_ratings'),
            func.avg(Ratings.rate).label('avg_rating'),
            func.min(Ratings.created_at).label('first_rating'),
            func.max(Ratings.created_at).label('last_rating')
        ).filter(
            Ratings.user_id == user_id
        ).first()
        
        return {
            'total_ratings': stats.total_ratings or 0,
            'avg_rating': float(stats.avg_rating or 0),
            'first_rating': stats.first_rating,
            'last_rating': stats.last_rating
        }
    
    def _get_user_favorite_brands(self, user_id: int) -> List[str]:
        from sqlalchemy import desc
        brand_stats = self.db.query(
            Perfume.brand,
            func.avg(Ratings.rate).label('avg_rating'),
            func.count(Ratings.id).label('rating_count')
        ).join(
            Ratings, Perfume.id == Ratings.perfume_id
        ).filter(
            Ratings.user_id == user_id,
            Perfume.brand.isnot(None)
        ).group_by(
            Perfume.brand
        ).order_by(
            desc('avg_rating'),
            desc('rating_count')
        ).limit(5).all()
        
        return [brand for brand, _, _ in brand_stats]