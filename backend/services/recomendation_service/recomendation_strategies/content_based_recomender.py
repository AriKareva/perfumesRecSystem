from typing import List, Dict, Any, Optional, Set
import numpy as np
from collections import defaultdict
from .base_recomendation import BaseRecommenderStrategy, RecommendationItem

class ContentBasedStrategy(BaseRecommenderStrategy):
    def __init__(self):
        super().__init__(
            name='content_based',
            description='Рекомендации на основе схожести признаков парфюмов'
        )
        self.data_provider = None
        self.feature_weights = {
            'brand': 0.3,
            'intensity': 0.3,
            'price_category': 0.1,
            'notes': 0.15 
        }
        self._perfume_vectors = {}  # кеш векторов признаков
    
    def setup(self, data_provider) -> None:
        self.data_provider = data_provider
        self._setup_done = True
    
    def can_recommend(self, user_id: int, data_provider = None) -> bool:
        if not self._setup_done and data_provider:
            self.setup(data_provider)
        
        if not self.data_provider:
            return False
            
        user_ratings = self.data_provider.get_user_ratings(user_id)
        return len(user_ratings) >= 3
    
    def get_requirements(self) -> Dict[str, Any]:
        base_reqs = super().get_requirements()
        base_reqs.update({
            'min_user_ratings': 3,
            'supports_new_items': True,  # может рекомендовать новые парфюмы
            'feature_weights': self.feature_weights
        })
        return base_reqs
    
    def recommend(
        self, 
        user_id: int, 
        top_n: int = 10,
        exclude_rated: bool = True,
        **kwargs
    ) -> List[RecommendationItem]:
        
        print(f"ContentBased: {user_id}")
        
        user_ratings = self.data_provider.get_user_ratings(user_id)
        if not user_ratings:
            return self._get_fallback_recommendations(top_n)

        rated_perfume_ids = [r['perfume_id'] for r in user_ratings]
        rated_perfumes = set(rated_perfume_ids)

        user_profile = self._build_user_profile(rated_perfume_ids, user_ratings)
        
        all_perfumes = self.data_provider.get_all_perfumes()
        
        similarities = []
        for perfume in all_perfumes:
            perfume_id = perfume['id']
            
            if exclude_rated and perfume_id in rated_perfumes:
                continue
            
            perfume_vector = self._get_perfume_vector(perfume_id, perfume)
            if perfume_vector is None:
                continue
            
            similarity = self._calculate_similarity(user_profile, perfume_vector)
            
            if similarity > 0:
                similarities.append((perfume_id, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for perfume_id, score in similarities[:top_n]:

            explanation = self._generate_explanation(
                user_profile, 
                perfume_id, 
                score
            )
            
            recommendations.append(
                RecommendationItem(
                    perfume_id=perfume_id,
                    score=float(score),
                    confidence=min(score * 2, 1.0)
                )
            )
        
        return recommendations
    
    def _build_user_profile(self, perfume_ids: List[int], user_ratings: List[Dict]) -> Dict[str, Any]:
        profile = {
            'brand_preferences': defaultdict(float),
            'intensity_preferences': defaultdict(float),
            'price_preferences': defaultdict(float),
            'notes_preferences': defaultdict(float),
            'total_weight': 0
        }
        
        for rating in user_ratings:
            perfume_id = rating['perfume_id']
            rating_score = rating['rating']  # 1-5
            
            features = self.data_provider.get_perfume_features(perfume_id)
            if not features:
                continue

            weight = rating_score / 5.0
            
            # агрегируем предпочтения
            if features.get('brand'):
                profile['brand_preferences'][features['brand']] += weight
            if features.get('gender'):
                profile['gender_preferences'][features['gender']] += weight
            if features.get('season'):
                for season in features['season']:
                    profile['season_preferences'][season] += weight
            if features.get('intensity'):
                profile['intensity_preferences'][features['intensity']] += weight
            if features.get('price_category'):
                profile['price_preferences'][features['price_category']] += weight
            if features.get('notes'):
                for note_type, notes in features['notes'].items():
                    for note in notes:
                        profile['notes_preferences'][note] += weight
            
            profile['total_weight'] += weight
        

        if profile['total_weight'] > 0:
            for key in ['brand', 'gender', 'season', 'intensity', 'price', 'notes']:
                pref_key = f'{key}_preferences'
                for pref in profile[pref_key]:
                    profile[pref_key][pref] /= profile['total_weight']
        
        return profile
    
    def _get_perfume_vector(self, perfume_id: int, perfume_data: Dict = None) -> Optional[Dict]:
        if perfume_id in self._perfume_vectors:
            return self._perfume_vectors[perfume_id]
        
        if perfume_data is None:
            features = self.data_provider.get_perfume_features(perfume_id)
        else:
            features = perfume_data
        
        if not features:
            return None
        
        vector = {}
        
        if features.get('brand'):
            vector['brand'] = {features['brand']: 1.0}
        if features.get('intensity'):
            vector['intensity'] = {features['intensity']: 1.0}
        if features.get('price_category'):
            vector['price_category'] = {features['price_category']: 1.0}
        if features.get('notes'):
            notes_dict = {}
            for note_type, notes in features['notes'].items():
                for note in notes:
                    notes_dict[note] = 1.0
            vector['notes'] = notes_dict
        
        self._perfume_vectors[perfume_id] = vector
        return vector
    
    def _calculate_similarity(
        self, 
        user_profile: Dict, 
        perfume_vector: Dict
    ) -> float:
        total_similarity = 0.0
        total_weight = 0.0
        
        for feature_type, weight in self.feature_weights.items():
            user_pref_key = f'{feature_type}_preferences'
            perfume_feat_key = feature_type
            
            if user_pref_key in user_profile and perfume_feat_key in perfume_vector:

                feature_similarity = self._calculate_feature_similarity(
                    user_profile[user_pref_key],
                    perfume_vector[perfume_feat_key]
                )
                
                total_similarity += feature_similarity * weight
                total_weight += weight
        
        return total_similarity / total_weight if total_weight > 0 else 0
    
    def _calculate_feature_similarity(
        self, 
        user_preferences: Dict[str, float], 
        perfume_features: Dict[str, float]
    ) -> float:
        if not user_preferences or not perfume_features:
            return 0.0
        
        similarity = 0.0
        for feature, perfume_weight in perfume_features.items():
            if feature in user_preferences:
                similarity += user_preferences[feature] * perfume_weight
        
        max_similarity = sum(perfume_features.values())
        return similarity / max_similarity if max_similarity > 0 else 0
    