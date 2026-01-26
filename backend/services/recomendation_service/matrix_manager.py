import datetime
import hashlib
import logging
from pathlib import Path
import pickle
from typing import Dict, Union
from ratings.models import Ratings
from fastapiu import Session, Depends, Optional
from db.connection import get_db
from scipy.sparse import csr_matrix, csc_matrix
import numpy as np
from scipy.sparse import save_npz
from sqlalchemy import func

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MatrixManager:
    def __init__(self, db: Session = Depends(get_db), 
                 storage_path: str = "./data/matrices"):
        
        self.db = db
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.rating_csr_matrix = Optional[csr_matrix] = None
        self.rating_csc_matrix = Optional[csr_matrix] = None

        # Маппинги ID ↔ индекс
        self.user_mapping: Dict[int, int] = {}  # user_id → row_index
        self.perfume_mapping: Dict[int, int] = {}  # perfume_id → col_index
        self.reverse_user_mapping: Dict[int, int] = {}  # row_index → user_id
        self.reverse_perfume_mapping: Dict[int, int] = {}  # col_index → perfume_id

        self.metadata = {
            'created_at': None,
            'last_updated': None,
            'data_hash': None,
            'version': '1.0'
        }

        self.stats = {
            'n_users': 0,
            'n_perfumes': 0,
            'n_ratings': 0,
            'sparsity': 0.0, 
            'avg_ratings_per_user': 0.0,
            'avg_ratings_per_perfume': 0.0,
            'rating_distribution': {}
        }
        
        # Кеширование для быстрого доступа
        self._similarity_cache = {}
        self._neighborhood_cache = {}
        self._cache_expiry = {}
        
    def create_matrix(
            self, 
            format_csr : bool = True,
            force_rebuild : bool = False,
            incremental_update : bool = True
    ) -> Union[csr_matrix, csc_matrix]: # используем такой формат для хранения только ненулевых строк/колонок
        rebuild = (
            force_rebuild or
            self.rating_csc_matrix is None or
            not self._is_matrix_data_fresh() or
            self._has_changes
        )

        # если не нужно переестраивать или обновлять инкрементом
        if not rebuild and incremental_update:
            try:
                self._update_matrix_increment
                logger.info('Обновление матрицы оценок')
        # если не удалось обновить, строим матрицу заново 
            except Exception as e:
                logger.warning('Не удалось обнонвить матрицу оценок')
                rebuild = True

        if rebuild:
            logger.info('Загрузка матрицы из БД')
            self.load_matrix_from_db()

        if format_csr:
            matrix = self.rating_csr_matrix
        else:
            if self.rating_csc_matrix is None:
                self.rating_csc_matrix = self.rating_csr_matrix.tocsc()
                
            matrix = self.rating_csc_matrix

        return matrix

    def load_matrix_from_db(self):
        # используем не всех пользователей и парфюмы для экономии памяти
        # однако позже следует добавить дугие рекомендательные методы,
        # чтобы пространство возможных рекомендаций не снижалось
        users_with_rates = self.db.query(Ratings.user_id).distinct().order_by(Ratings.user_id).all()
        perfumes_with_rates = self.db.query(Ratings.perfume_id).distinct().order_by(Ratings.perfume_id).all()

        # маппинги
        self.user_mapping = {user_id: idx for idx, (user_id,) in enumerate(users_with_rates)}
        self.perfume_mapping = {perfume_id: idx for idx, (perfume_id,) in enumerate(perfumes_with_rates)}
        self.reverse_user_mapping = {v: k for k, v in self.user_mapping.items()}
        self.reverse_perfume_mapping = {v: k for k, v in self.perfume_mapping.items()}

        data = []
        rows = []
        cols = []

        batch_size = 50000
        offset = 0

        while True:
            batch = self.db.query(Ratings).limit(batch_size).offset(offset).all()
            if not batch:
                break
                
            for rating in batch:
                user_idx = self.user_mapping.get(rating.user_id)
                perfume_idx = self.perfume_mapping.get(rating.perfume_id)
                
                if user_idx is not None and perfume_idx is not None:
                    data.append(rating.rate)
                    rows.append(user_idx)
                    cols.append(perfume_idx)
            
            offset += batch_size
            logger.debug(f'Обработано {offset} записей...')

        n_users = len(users_with_rates)
        n_perfumes = len(perfumes_with_rates)
        
        self.rating_matrix = csr_matrix(
            (data, (rows, cols)),
            shape=(n_users, n_perfumes),
            dtype=np.float32
        )

        self._save_to_disk()

        logger.info(f"Матрица построена. Пользователей: {n_users}, парфюмов: {n_perfumes}")

    def _update_matrix_increment(self):
        # Получаем последние оценки, которых нет в текущей матрице
        last_update = self.metadata['last_updated'] or datetime.min
        
        new_ratings = self.db.query(Ratings).filter(
            Ratings.created_at > last_update
        ).all()
        
        if not new_ratings:
            logger.debug("Нет новых оценок для инкрементального обновления")
            return
        
        logger.info(f"Инкрементальное обновление: {len(new_ratings)} новых оценок")
        
        # Обновляем матрицу
        for rating in new_ratings:
            user_idx = self.user_mapping.get(rating.user_id)
            perfume_idx = self.perfume_mapping.get(rating.perfume_id)
            
            # Если новый пользователь или парфюм - требуется полное перестроение
            if user_idx is None or perfume_idx is None:
                logger.warning("Обнаружен новый пользователь или парфюм, требуется полное перестроение")
                self._build_from_scratch()
                return
            
            # Обновляем существующую ячейку
            self.rating_matrix[user_idx, perfume_idx] = rating.rate
        
        logger.info("Инкрементальное обновление завершено")
    
    def _is_matrix_data_fresh(self):
        if not self.metadata['last_updated']:
            return False
        
        # Матрица считается устаревшей, если ей больше суток
        stale_threshold = datetime.timedelta(days=1)
        return ~(datetime.now() - self.metadata['last_updated'] > stale_threshold)

    def _compute_data_hash(self):
        # Используем агрегированные данные для вычисления хеша
        rating_stats = self.db.query(
            func.count(Ratings.id).label('count'),
            func.max(Ratings.created_at).label('max_date')
        ).first()
        
        hash_data = f"{rating_stats.count}_{rating_stats.max_date}"
        return hashlib.md5(hash_data.encode()).hexdigest()

    def _has_changes(self):
        current_hash = self._compute_data_hash()
        
        # Если это первая загрузка
        if not self.metadata['data_hash']:
            self.metadata['data_hash'] = current_hash
            return True
        
        # Сравниваем хеши
        return current_hash != self.metadata['data_hash']

    def load_to_disk(self):
        if self.rating_csc_matrix is None:
            return
        
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        matrix_path = f'{self.storage_path}_csc_matrix_{ts}'
        save_npz(matrix_path, self.rating_csc_matrix)

        metadata_path = self.storage_path / f"metadata_{ts}.pkl"
        metadata = {
            'user_mapping': self.user_mapping,
            'perfume_mapping': self.perfume_mapping,
            'metadata': self.metadata,
            'stats': self.stats
        }

        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        # Симлинк 
        latest_matrix = self.storage_path / "_csc_matrix_latest.npz"
        latest_metadata = self.storage_path / "metadata_latest.pkl"
        
        if latest_matrix.exists():
            latest_matrix.unlink()
        if latest_metadata.exists():
            latest_metadata.unlink()
        
        latest_matrix.symlink_to(matrix_path.name)
        latest_metadata.symlink_to(metadata_path.name)
        
        logger.info(f"Матрица сохранена: {matrix_path}")

    def _cleanup_old_versions(self, max_versions: int = 5):
        matrix_files = sorted(
            self.storage_path.glob("rating_matrix_*.npz"),
            key=lambda x: x.name  # Сортировка по имени = по времени
        )
        
        metadata_files = sorted(
            self.storage_path.glob("metadata_*.pkl"),
            key=lambda x: x.name
        )
        for files in (matrix_files, metadata_files):
            if len(files) > max_versions:
                for old_file in files[:-max_versions]:
                    # Не удаляем файлы, на которые ссылаются симлинки
                    if not old_file.is_symlink():
                        old_file.unlink()
                        logger.debug(f"Удалён старый файл: {old_file.name}")