from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np
from dataclasses import dataclass

@dataclass
class RecommendationItem:
    perfume_id: int
    score: float
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'perfume_id': self.perfume_id,
            'score': self.score,
            'confidence': self.confidence,
            'explanation': self.explanation or {}
        }

class BaseRecommenderStrategy(ABC):
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self._setup_done = False
    
    @abstractmethod
    def setup(self, data_provider) -> None:
        pass
    
    @abstractmethod
    def recommend(
        self, 
        user_id: int, 
        top_n: int = 10,
        exclude_rated: bool = True,
        **kwargs
    ) -> List[RecommendationItem]:
        pass
    
    def can_recommend(self, user_id: int, data_provider) -> bool:
        return True
    
    def get_requirements(self) -> Dict[str, Any]:
        return {
            'min_user_ratings': 0,
            'min_common_items': 0,
            'supports_new_users': True,
            'supports_new_items': True
        }
    
    def _get_fallback_recommendations(self, top_n: int) -> List[RecommendationItem]:
        try:
            all_perfumes = self.data_provider.get_all_perfumes()
            recommendations = []
            
            for perfume in all_perfumes[:top_n]:
                recommendations.append(
                    RecommendationItem(
                        perfume_id=perfume['id'],
                        score=3.5,
                        confidence=0.2,
                        explanation={
                            'method': self.name,
                            'reason': 'Популярные парфюмы (запасной вариант)',
                            'fallback': True
                        }
                    )
                )
            
            return recommendations
        except:
            return []
