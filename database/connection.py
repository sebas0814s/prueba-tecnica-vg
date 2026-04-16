from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from config.settings import settings


def get_engine() -> Engine:
    """Crea y retorna el motor de conexión a PostgreSQL."""
    return create_engine(settings.database_url)


def get_session() -> Session:
    """
    Retorna una sesión de base de datos lista para usar.
    Responsabilidad única: solo provee la sesión, no ejecuta queries.
    """
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()
