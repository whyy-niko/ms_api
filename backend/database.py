from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
import threading

# SQLite база данных
SQLALCHEMY_DATABASE_URL = "sqlite:///../museum.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Хранилище для SQL запросов (по потокам)
thread_local = threading.local()

def get_sql_queries():
    """Возвращает список SQL запросов для текущего потока"""
    if not hasattr(thread_local, 'sql_queries'):
        thread_local.sql_queries = []
    return thread_local.sql_queries

def clear_sql_queries():
    """Очищает список SQL запросов для текущего потока"""
    if hasattr(thread_local, 'sql_queries'):
        thread_local.sql_queries = []

def add_sql_query(query):
    """Добавляет SQL запрос в список для текущего потока"""
    if not hasattr(thread_local, 'sql_queries'):
        thread_local.sql_queries = []
    thread_local.sql_queries.append(query)

# Обработчик для логирования SQL запросов
@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Логирует SQL запросы перед выполнением"""
    sql_query = {
        'statement': statement,
        'parameters': parameters,
        'executemany': executemany
    }
    add_sql_query(sql_query)

def get_db():
    """Генератор сессии базы данных с очисткой SQL запросов"""
    clear_sql_queries()  # Очищаем запросы при каждом запросе
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()