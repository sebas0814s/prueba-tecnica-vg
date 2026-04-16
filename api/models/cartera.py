from typing import Optional
from pydantic import BaseModel


class CarteraFiltros(BaseModel):
    """
    Parámetros de filtro aceptados por el endpoint GET /cartera.
    Todos son opcionales para permitir consultas abiertas.

    Principio I (Segregación de interfaces): este modelo solo contiene
    lo que necesita el filtro, no mezcla con el modelo de respuesta.
    """
    entidad: Optional[str] = None
    tipo_cartera: Optional[str] = None
    periodo_desde: Optional[str] = None
    periodo_hasta: Optional[str] = None
    page: int = 1
    page_size: int = 50


class CarteraResponse(BaseModel):
    """
    Estructura de cada registro retornado por la API.
    Principio I: solo expone los campos que el cliente necesita ver.
    """
    id: int
    entidad: str
    tipo_cartera: str
    producto: str
    periodo: str
    saldo: Optional[float]

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    """Envuelve la lista de resultados con metadata de paginación."""
    total: int
    page: int
    page_size: int
    data: list[CarteraResponse]
