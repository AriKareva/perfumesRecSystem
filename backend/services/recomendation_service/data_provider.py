from typing import Union
from auth.user_service import get_current_user
from perfumes.perfumes_dao import PerfumeDAO
from users.users_dao import UserDAO
from ratings.models import Ratings
from ratings.schemas import RatingResponse
from services.recomendation_service.matrix_manager import MatrixManager
from db.connection import get_db
from users.models import Users
from fasapi import Session, Depends
from scipy.sparse import csr_matrix, csc_matrix


class DataProvider:
    def __init__(self, matrix_manager : MatrixManager,
                user_dao : UserDAO, 
                perfume_dao : PerfumeDAO):
        self._matrix_manager = matrix_manager
        self._user_dao = user_dao
        self._perfume_dao = perfume_dao 
    
    def get_rating_matrix(self, format_csr=False):
        return self._matrix_manager.create_matrix(format_csr)
    
    def get_user_similarity_matrix(self):
        return self._matrix_manager.get_user_similarity_matrix()
    
    def get_item_similarity_matrix(self):
        return self._matrix_manager.get_item_similarity_matrix()
    
    def get_user_ratings(self, user_id):
        return self._user_dao.get_ratings(user_id)
    
    def get_user_by_id(self, user_id):
        return self._user_dao.get_by_id(user_id)
    
    def get_perfume_features(self, perfume_id):
        return self._perfume_dao.get_features(perfume_id)
    
    def get_all_perfumes(self):
        return self._perfume_dao.get_all()