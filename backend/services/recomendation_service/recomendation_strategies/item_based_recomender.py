from typing import List, Dict, Any, Optional, Set
import numpy as np
from collections import defaultdict
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from .base_recomendation import BaseRecommenderStrategy, RecommendationItem


class ItemBasedStrategy(BaseRecommenderStrategy):
    def __init__(self):
        super().__init__(
            name='item_based_cf',
            description='Рекомендации на основе схожести парфюмов (коллаборативная фильтрация)'
        )
        self.data_provider = None
        self.min_similarity = 0.1
        self.k_neighbors = 50
        self._item_similarity_cache = {}
        self._perfume_vectors_cache = {}
    
    def setup(self, data_provider) -> None:
        self.data_provider = data_provider
        self._setup_done = True
        print(f"ItemBasedStrategy setup complete")
    
    def can_recommend(self, user_id: int, data_provider = None) -> bool:
        if not self._setup_done and data_provider:
            self.setup(data_provider)
        
        if not self.data_provider:
            return False
            
        user_ratings = self.data_provider.get_user_ratings(user_id)
        return len(user_ratings) >= 2
    
    def get_requirements(self) -> Dict[str, Any]:
        base_reqs = super().get_requirements()
        base_reqs.update({
            'min_user_ratings': 2,
            'min_common_items': 0,
            'supports_new_users': False,
            'supports_new_items': False,
            'similarity_threshold': self.min_similarity,
            'neighbors_count': self.k_neighbors
        })
        return base_reqs
    
    def recommend(
        self, 
        user_id: int, 
        top_n: int = 10,
        exclude_rated: bool = True,
        **kwargs
    ) -> List[RecommendationItem]:
        
        print(f"ItemBasedStrategy: {user_id}")
        
        user_ratings = self.data_provider.get_user_ratings(user_id)
        if not user_ratings:
            return self._get_fallback_recommendations(top_n)
        
        # Получаем матрицу оценок
        rating_matrix = self.data_provider.get_rating_matrix(format_csr=True)
        matrix_manager = self.data_provider._matrix_manager
        
        # Маппинги ID - индекс
        perfume_mapping = matrix_manager.perfume_mapping
        reverse_perfume_mapping = matrix_manager.reverse_perfume_mapping
        
        # Собираем оценки пользователя
        rated_items = {}
        user_rated_ids = set()
        for rating in user_ratings:
            perfume_id = rating['perfume_id']
            user_rated_ids.add(perfume_id)
            if perfume_id in perfume_mapping:
                idx = perfume_mapping[perfume_id]
                rated_items[idx] = rating['rating']
        
        if not rated_items:
            return self._get_fallback_recommendations(top_n)
        
        # Вычисляем или получаем матрицу схожести
        item_sim_matrix = self._get_item_similarity_matrix(rating_matrix)
        
        # Предсказываем оценки
        predictions = self._predict_ratings(
            rated_items, 
            item_sim_matrix, 
            reverse_perfume_mapping,
            exclude_rated=exclude_rated,
            user_rated_ids=user_rated_ids
        )
        
        # Сортируем и выбираем топ-N
        sorted_predictions = sorted(
            predictions.items(), 
            key=lambda x: x[1]['score'], 
            reverse=True
        )
        
        recommendations = []
        for perfume_id, pred_data in sorted_predictions[:top_n]:
            explanation = self._generate_explanation(
                user_id, 
                perfume_id, 
                pred_data
            )
            
            recommendations.append(
                RecommendationItem(
                    perfume_id=perfume_id,
                    score=float(pred_data['score']),
                    confidence=float(pred_data['confidence']),
                    explanation=explanation
                )
            )
        
        return recommendations
    
    def _get_item_similarity_matrix(self, rating_matrix: csr_matrix) -> csr_matrix:
        cache_key = 'item_similarity'
        
        if cache_key in self._item_similarity_cache:
            return self._item_similarity_cache[cache_key]
        
        # Пытаемся получить предвычисленную матрицу
        try:
            item_sim_matrix = self.data_provider.get_item_similarity_matrix()
            if item_sim_matrix is not None:
                self._item_similarity_cache[cache_key] = item_sim_matrix
                return item_sim_matrix
        except Exception as e:
            print(f"Не удалось получить предвычисленную матрицу схожести: {e}")
        
        # Вычисляем схожесть самостоятельно
        print("Вычисление матрицы схожести парфюмов...")
        
        # Транспонируем для работы с парфюмами
        item_matrix = rating_matrix.T.astype(np.float32)
        
        # Нормализуем (убираем среднее)
        item_means = item_matrix.mean(axis=1)
        item_matrix_normalized = item_matrix - item_means.reshape(-1, 1)
        
        # Вычисляем косинусную схожесть
        similarity = cosine_similarity(item_matrix_normalized, dense_output=False)
        
        # Кешируем результат
        self._item_similarity_cache[cache_key] = similarity
        
        return similarity
    
    def _predict_ratings(
        self,
        rated_items: Dict[int, float],
        similarity_matrix: csr_matrix,
        reverse_mapping: Dict[int, int],
        exclude_rated: bool = True,
        user_rated_ids: Set[int] = None
    ) -> Dict[int, Dict[str, Any]]:
        predictions = {}
        
        # Для каждого оцененного парфюма
        for rated_idx, rating in rated_items.items():
            # Получаем схожести с другими парфюмами
            similarities = similarity_matrix[rated_idx].toarray().flatten()
            
            # Находим индексы схожих парфюмов
            similar_indices = np.where(similarities >= self.min_similarity)[0]
            
            for item_idx in similar_indices:
                # Пропускаем сам парфюм
                if item_idx == rated_idx:
                    continue
                
                # Получаем ID парфюма
                perfume_id = reverse_mapping.get(item_idx)
                if not perfume_id:
                    continue
                
                # Пропускаем уже оцененные
                if exclude_rated and user_rated_ids and perfume_id in user_rated_ids:
                    continue
                
                similarity = similarities[item_idx]
                
                if perfume_id not in predictions:
                    predictions[perfume_id] = {
                        'weighted_sum': 0.0,
                        'similarity_sum': 0.0,
                        'source_items': []
                    }
                
                predictions[perfume_id]['weighted_sum'] += rating * similarity
                predictions[perfume_id]['similarity_sum'] += similarity
                predictions[perfume_id]['source_items'].append({
                    'source_perfume': reverse_mapping.get(rated_idx),
                    'similarity': float(similarity),
                    'rating': rating
                })
        
        # Вычисляем итоговые оценки
        final_predictions = {}
        for perfume_id, data in predictions.items():
            if data['similarity_sum'] > 0:
                # Взвешенное среднее
                score = data['weighted_sum'] / data['similarity_sum']
                
                # Нормализуем к 0-5
                score = max(0.0, min(5.0, score))
                
                # Уверенность на основе силы схожести
                avg_similarity = data['similarity_sum'] / len(data['source_items'])
                confidence = min(1.0, avg_similarity * 2)
                
                final_predictions[perfume_id] = {
                    'score': score,
                    'confidence': confidence,
                    'sources': data['source_items']
                }
        
        return final_predictions