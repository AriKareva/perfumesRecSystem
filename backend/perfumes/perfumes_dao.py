from typing import List, Optional
from perfumes.schemas import Perfume
from ratings.models import Ratings
from sqlalchemy import Session
from sqlalchemy import func, desc

class PerfumeDAO:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_by_id(self, perfume_id: int) -> Optional[Perfume]:
        return self.db.query(Perfume).filter(Perfume.id == perfume_id).first()
    
    def get_all(self, limit: int = 1000) -> List[Perfume]:
        return self.db.query(Perfume)\
            .order_by(Perfume.id)\
            .limit(limit)\
            .all()
    
    def search_by_name(self, name: str, limit: int = 50) -> List[Perfume]:
        return self.db.query(Perfume)\
            .filter(Perfume.name.ilike(f'%{name}%'))\
            .order_by(Perfume.name)\
            .limit(limit)\
            .all()
    
    def get_by_brand(self, brand: str, limit: int = 100) -> List[Perfume]:
        return self.db.query(Perfume)\
            .filter(Perfume.brand == brand)\
            .order_by(Perfume.name)\
            .limit(limit)\
            .all()
    
    def get_popular(self, limit: int = 50) -> List[Perfume]:
        popular_ids = self.db.query(
            Ratings.perfume_id,
            func.count(Ratings.id).label('rating_count')
        ).group_by(
            Ratings.perfume_id
        ).order_by(
            desc('rating_count')
        ).limit(limit).all()
        
        perfume_ids = [pid for pid, _ in popular_ids]
        
        if not perfume_ids:
            return []
        
        return self.db.query(Perfume)\
            .filter(Perfume.id.in_(perfume_ids))\
            .all()