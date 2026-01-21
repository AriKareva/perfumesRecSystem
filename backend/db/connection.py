import os
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager


# настройка логирования
logger = logging.getLogger(__name__)


Base = declarative_base()

db_url = os.getenv('DATABASE_URL')

# параметры пула соединений
POOL_CONFIG = {
    "poolclass": QueuePool,
    "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),      # Количество постоянных соединений
    "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")), # Дополнительные соединения при нагрузке
    "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")), # Таймаут ожидания соединения (сек)
    "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "3600")), # Пересоздавать соединения каждый час
    "pool_pre_ping": os.getenv("DB_POOL_PRE_PING", "true").lower() == "true", # Проверять перед использованием
    "echo": os.getenv("DB_ECHO", "false").lower() == "true", # Логировать SQL
}

db_engine = create_engine(db_url, **POOL_CONFIG)

SessionLocal = sessionmaker(
    bind=db_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

def init_db():
    logger.info('Создание таблиц БД')
    try:
        # Base.metadata.drop_all(bind=db_engine)
        Base.metadata.create_all(bind=db_engine)
        logger.info('Таблицы БД пересозданы')
    
    except Exception as e:
        logger.error(f'Ошибка при создании таблиц: {e}')
        raise


def get_db():
    session = SessionLocal()

    try:
        yield session
        session.commit()
        logger.info(f'Транзакция выполнена')

    except Exception as e:
        session.rollback()
        logger.error(f'Ошибка транзакции: {e}')
        raise

    finally:
        session.close()
        logger.debug(f'Сессия закрыта')