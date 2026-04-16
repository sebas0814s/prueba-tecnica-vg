from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Centraliza todas las variables de configuración del proyecto.
    Los valores se leen automáticamente desde el archivo .env.
    """

    # Conexión a PostgreSQL
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "cartera_db"
    db_user: str = "postgres"
    db_password: str = ""

    # Ruta al archivo CSV exportado de datos.gov.co
    csv_path: str = "data/cartera.csv"

    @property
    def database_url(self) -> str:
        """Construye la URL de conexión para SQLAlchemy."""
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instancia única reutilizable en todo el proyecto (patrón Singleton simple)
settings = Settings()
