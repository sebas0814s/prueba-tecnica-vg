"""
database/connection.py
----------------------
Este archivo maneja la conexión a la base de datos PostgreSQL.

Piénsalo como el "puente" entre el código Python y la base de datos.
Cada vez que alguien necesita leer o escribir datos, pide una sesión
a través de este módulo.

Se usa SQLAlchemy, que es una librería que nos permite hablar con
la base de datos usando Python en lugar de escribir SQL directamente.
"""

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from config.settings import settings


def get_engine() -> Engine:
    """
    Crea el motor de conexión a PostgreSQL.

    El 'motor' es el objeto principal que sabe cómo hablar con la base
    de datos. Se configura con la URL que armamos en settings.py.
    """
    return create_engine(settings.database_url)


def get_session() -> Session:
    """
    Abre y retorna una sesión activa con la base de datos.

    Una 'sesión' es como abrir una conversación con la base de datos:
    puedes hacer preguntas (queries) y cuando terminas la cierras.

    Importante: quien llama a esta función es responsable de cerrar
    la sesión cuando ya no la necesite (session.close()).
    """
    engine = get_engine()

    # sessionmaker es una fábrica: cada vez que la llamamos nos da
    # una sesión nueva lista para usar.
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()
