"""
api/models/cartera.py
---------------------
Define la "forma" de los datos que entran y salen de la API.

Pydantic es una librería que valida automáticamente los datos.
Si alguien envía un tipo incorrecto (ej: texto donde se espera número),
Pydantic lo detecta y devuelve un error claro antes de que llegue
a la base de datos.

Hay tres modelos en este archivo, cada uno con una responsabilidad distinta:
    1. CarteraFiltros   → qué parámetros acepta el endpoint de consulta
    2. CarteraResponse  → cómo se ve cada registro en la respuesta
    3. PaginatedResponse → envuelve la lista con información de paginación
"""

from typing import Optional
from pydantic import BaseModel


class CarteraFiltros(BaseModel):
    """
    Parámetros opcionales que el usuario puede enviar para filtrar resultados.

    Todos son opcionales (= None por defecto), lo que significa que si no
    se envía ninguno, la API devuelve todos los registros.

    Ejemplos de uso:
        ?entidad=Bancolombia
        ?tipo_cartera=CONSUMO&periodo_desde=2022-01&periodo_hasta=2023-12
    """
    entidad:       Optional[str] = None   # Nombre parcial o completo de la entidad
    tipo_cartera:  Optional[str] = None   # Tipo de cartera (comercial, consumo, etc.)
    periodo_desde: Optional[str] = None   # Fecha inicio en formato YYYY-MM
    periodo_hasta: Optional[str] = None   # Fecha fin en formato YYYY-MM
    page:          int = 1                # Número de página (empieza en 1)
    page_size:     int = 50               # Cuántos registros devolver por página


class CarteraResponse(BaseModel):
    """
    Estructura de cada registro que devuelve la API.

    Solo incluye los campos que el cliente necesita ver.
    Campos internos de la base de datos (como created_at) no se exponen.

    from_attributes = True le dice a Pydantic que puede leer los valores
    desde atributos de un objeto (no solo desde un diccionario).
    """
    id:           int             # Identificador único del registro en la BD
    entidad:      str             # Nombre de la entidad financiera
    tipo_cartera: str             # Categoría de la cartera
    producto:     str             # Producto específico dentro de la categoría
    periodo:      str             # Mes y año en formato YYYY-MM
    saldo:        Optional[float] # Saldo en pesos colombianos (puede ser nulo)

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    """
    Respuesta paginada que envuelve la lista de resultados.

    La paginación es importante cuando hay muchos registros: en lugar de
    devolver los 106,000 registros de golpe, los divide en "páginas"
    de N registros cada una.

    Ejemplo de respuesta:
    {
        "total": 106905,   ← total de registros que coinciden con los filtros
        "page": 1,         ← página actual
        "page_size": 50,   ← registros por página
        "data": [...]      ← lista de registros de esta página
    }
    """
    total:     int                    # Total de registros que coinciden con los filtros
    page:      int                    # Página actual
    page_size: int                    # Registros por página
    data:      list[CarteraResponse]  # Los registros de esta página
