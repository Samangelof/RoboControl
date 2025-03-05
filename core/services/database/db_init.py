import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.services.database.models import Base

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DB_PATH = f"sqlite:///{os.path.join(BASE_DIR, 'storage', 'documents_knp.db')}"
print(f'------------------------- {DB_PATH} -------------------------')

engine = create_engine(DB_PATH)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Глобальная сессия для упрощения доступа ---
db_session = SessionLocal()

def get_db():
    """Фабрика для получения активной сессии"""
    return db_session

def close_db():
    """Явное закрытие сессии"""
    db_session.close()

def init_db():
    """Создание таблиц в БД, если их нет"""
    Base.metadata.create_all(engine)
