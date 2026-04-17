"""
config/settings.py
------------------
Este archivo es el "panel de control" del proyecto.

En lugar de escribir contraseñas o rutas directamente en el código
(lo cual es una mala práctica de seguridad), se leen desde un archivo
llamado `.env` que cada desarrollador tiene en su máquina de forma local.

Así, el mismo código funciona en cualquier computador sin modificaciones.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Clase que representa todas las variables de configuración del proyecto.

    Pydantic lee automáticamente el archivo .env y asigna cada variable
    a su atributo correspondiente. Si una variable no está en .env,
    usa el valor por defecto que está escrito aquí.
    """

    # --- Datos de conexión a la base de datos PostgreSQL ---
    db_host: str = "localhost"   # Dirección del servidor (localhost = esta misma máquina)
    db_port: int = 5432          # Puerto por defecto de PostgreSQL
    db_name: str = "cartera_db"  # Nombre de la base de datos que creamos
    db_user: str = "postgres"    # Usuario administrador de PostgreSQL
    db_password: str = ""        # Contraseña (se lee del .env, no se escribe aquí)

    # --- Ruta del archivo de datos ---
    csv_path: str = "data/cartera.csv"  # Dónde está el CSV exportado de datos.gov.co

    @property
    def database_url(self) -> str:
        """
        Construye la URL de conexión completa para SQLAlchemy.

        SQLAlchemy necesita una URL con este formato para conectarse:
        postgresql://usuario:contraseña@servidor:puerto/base_de_datos
        """
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    class Config:
        # Le dice a Pydantic que lea las variables desde el archivo .env
        env_file = ".env"
        env_file_encoding = "utf-8"


# Creamos UNA SOLA instancia que se comparte en todo el proyecto.
# Esto evita leer el archivo .env múltiples veces (patrón Singleton).
settings = Settings()
