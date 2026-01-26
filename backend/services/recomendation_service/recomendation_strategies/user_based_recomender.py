from typing import List, Dict, Any, Optional, Set
import numpy as np
from collections import defaultdict
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from .base_recomendation import BaseRecommenderStrategy, RecommendationItem


class UserBasedStrategy(BaseRecommenderStrategy):
    def __init__(self):
        super().__init__(
            name='user_based',
            description='Рекомендации на основе схожести пользователей (коллаборативная фильтрация)'
        )
        self.data_provider = None
        self.min_similarity = 0.1
        self.k_neighbors = 30
        self._user_similarity_cache = {}
    
    def setup(self, data_provider) -> None:
        self.data_provider = data_provider
        self._setup_done = True
        print(f"UserBasedStrategy setup complete")
    
    def can_recommend(self, user_id: int, data_provider = None) -> bool:
        if not self._setup_done and data_provider:
            self.setup(data_provider)
        
        if not self.data_provider:
            return False
            
        # Проверяем, есть ли пользователь в матрице
        matrix_manager = self.data_provider._matrix_manager
        return user_id in matrix_manager.user_mapping
    
    def get_requirements(self) -> Dict[str, Any]:
        base_reqs = super().get_requirements()
        base_reqs.update({
            'min_user_ratings': 1,
            'min_common_items': 0,
            'supports_new_users': False,
            'supports_new_items': True,
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
        
        print(f"UserBasedStrategy: {user_id}")
        
        # Проверяем наличие пользователя в системе
        matrix_manager = self.data_provider._matrix_manager
        if user_id not in matrix_manager.user_mapping:
            return self._get_fallback_recommendations(top_n)
        
        user_idx = matrix_manager.user_mapping[user_id]
        
        # Получаем оценки пользователя
        user_ratings = self.data_provider.get_user_ratings(user_id)
        user_rated_ids = {r['perfume_id'] for r in user_ratings}
        
        # Получаем матрицу оценок
        rating_matrix = self.data_provider.get_rating_matrix(format_csr=True)
        
        # Получаем матрицу схожести пользователей
        user_sim_matrix = self._get_user_similarity_matrix(rating_matrix)
        
        # Находим схожих пользователей
        similar_users = self._find_similar_users(
            user_idx, 
            user_sim_matrix, 
            matrix_manager.reverse_user_mapping
        )
        
        if not similar_users:
            return self._get_fallback_recommendations(top_n)
        
        # Собираем оценки схожих пользователей
        neighbor_predictions = self._collect_neighbor_ratings(
            similar_users,
            matrix_manager,
            exclude_rated=exclude_rated,
            user_rated_ids=user_rated_ids
        )
        
        # Вычисляем финальные предсказания
        final_predictions = self._compute_predictions(neighbor_predictions)
        
        # Сортируем и выбираем топ-N
        sorted_predictions = sorted(
            final_predictions.items(), 
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
    
    def _get_user_similarity_matrix(self, rating_matrix: csr_matrix) -> csr_matrix:
        cache_key = 'user_similarity'
        
        if cache_key in self._user_similarity_cache:
            return self._user_similarity_cache[cache_key]
        
        # Пытаемся получить предвычисленную матрицу
        try:
            user_sim_matrix = self.data_provider.get_user_similarity_matrix()
            if user_sim_matrix is not None:
                self._user_similarity_cache[cache_key] = user_sim_matrix
                return user_sim_matrix
        except Exception as e:
            print(f"Не удалось получить предвычисленную матрицу схожести: {e}")
        
        # Вычисляем схожесть самостоятельно
        print("Вычисление матрицы схожести пользователей...")
        
        # Нормализуем матрицу оценок
        user_means = rating_matrix.mean(axis=1)
        rating_matrix_normalized = rating_matrix - user_means.reshape(-1, 1)
        
        # Вычисляем косинусную схожесть
        similarity = cosine_similarity(rating_matrix_normalized, dense_output=False)
        
        # Кешируем результат
        self._user_similarity_cache[cache_key] = similarity
        
        return similarity
    
    def _find_similar_users(
        self,
        user_idx: int,
        similarity_matrix: csr_matrix,
        reverse_mapping: Dict[int, int]
    ) -> List[Dict[str, Any]]:

        # Получаем схожести для текущего пользователя
        similarities = similarity_matrix[user_idx].toarray().flatten()
        
        # Ищем пользователей с достаточной схожестью (исключая самого себя)
        similar_indices = np.where(
            (similarities >= self.min_similarity) & 
            (np.arange(len(similarities)) != user_idx)
        )[0]
        
        # Сортируем по схожести и берем топ-K
        top_indices = sorted(
            similar_indices, 
            key=lambda x: similarities[x], 
            reverse=True
        )[:self.k_neighbors]
        
        # Формируем список схожих пользователей
        similar_users = []
        for idx in top_indices:
            similar_users.append({
                'user_id': reverse_mapping[idx],
                'similarity': float(similarities[idx]),
                'index': idx
            })
        
        return similar_users
    
    def _collect_neighbor_ratings(
        self,
        similar_users: List[Dict[str, Any]],
        matrix_manager,
        exclude_rated: bool = True,
        user_rated_ids: Set[int] = None
    ) -> Dict[int, Dict[str, Any]]:

        neighbor_ratings = {}
        
        for neighbor in similar_users:
            neighbor_id = neighbor['user_id']
            similarity = neighbor['similarity']
            
            # Получаем оценки соседа
            neighbor_ratings_list = self.data_provider.get_user_ratings(neighbor_id)
            
            for rating in neighbor_ratings_list:
                perfume_id = rating['perfume_id']
                
                # Пропускаем если парфюм не в матрице
                if perfume_id not in matrix_manager.perfume_mapping:
                    continue
                
                # Пропускаем уже оцененные пользователем
                if exclude_rated and user_rated_ids and perfume_id in user_rated_ids:
                    continue
                
                if perfume_id not in neighbor_ratings:
                    neighbor_ratings[perfume_id] = {
                        'weighted_sum': 0.0,
                        'similarity_sum': 0.0,
                        'neighbors': []
                    }
                
                neighbor_ratings[perfume_id]['weighted_sum'] += rating['rating'] * similarity
                neighbor_ratings[perfume_id]['similarity_sum'] += similarity
                neighbor_ratings[perfume_id]['neighbors'].append({
                    'user_id': neighbor_id,
                    'similarity': similarity,
                    'rating': rating['rating']
                })
        
        return neighbor_ratings
    
    def _compute_predictions(
        self, 
        neighbor_ratings: Dict[int, Dict[str, Any]]
    ) -> Dict[int, Dict[str, Any]]:

        predictions = {}
        
        for perfume_id, data in neighbor_ratings.items():
            if data['similarity_sum'] > 0:
                # Взвешенное среднее
                score = data['weighted_sum'] / data['similarity_sum']
                
                # Нормализуем к 0-5
                score = max(0.0, min(5.0, score))
                
                # Уверенность на основе силы схожести и количества соседей
                avg_similarity = data['similarity_sum'] / len(data['neighbors'])
                confidence = min(1.0, avg_similarity * 1.5)
                
                predictions[perfume_id] = {
                    'score': score,
                    'confidence': confidence,
                    'neighbors': data['neighbors']
                }
        
        return predictions
    