"""
api/routes/cartera.py
---------------------
Define los tres endpoints (URLs) que expone la API.

Un endpoint es una dirección web que responde cuando alguien hace
una petición HTTP. Por ejemplo:
    GET http://localhost:8000/cartera?entidad=Bancolombia

FastAPI se encarga automáticamente de:
    - Leer los parámetros de la URL
    - Validarlos con Pydantic
    - Generar la documentación en /docs
    - Convertir la respuesta a JSON

Los endpoints disponibles son:
    GET /cartera           → consulta con filtros y paginación
    GET /cartera/entidades → lista de entidades financieras
    GET /cartera/tipos     → lista de tipos de cartera
"""

from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from api.models.cartera import CarteraResponse, PaginatedResponse
from api.repositories.cartera_repo import PostgreSQLCarteraRepository


# APIRouter agrupa los endpoints bajo el prefijo /cartera
# El tag "Cartera Financiera" los agrupa visualmente en la documentación /docs
router = APIRouter(prefix="/cartera", tags=["Cartera Financiera"])

# Instancia del repositorio que usaremos para consultar la base de datos.
# Al depender de la clase base abstracta (no de PostgreSQL directamente),
# podríamos cambiar la BD sin tocar ninguna línea de los endpoints.
_repo = PostgreSQLCarteraRepository()


@router.get("", response_model=PaginatedResponse, summary="Consultar registros de cartera")
def get_cartera(
    entidad:       Optional[str] = Query(None, description="Nombre parcial o exacto de la entidad financiera"),
    tipo_cartera:  Optional[str] = Query(None, description="Tipo de cartera (ej: CONSUMO, VIVIENDA VIS PESOS)"),
    periodo_desde: Optional[str] = Query(None, description="Periodo inicial en formato YYYY-MM (ej: 2022-01)"),
    periodo_hasta: Optional[str] = Query(None, description="Periodo final en formato YYYY-MM (ej: 2024-12)"),
    page:          int           = Query(1,    ge=1,        description="Número de página (empieza en 1)"),
    page_size:     int           = Query(50,   ge=1, le=500, description="Registros por página (máximo 500)"),
):
    """
    Devuelve registros de distribución de cartera con filtros opcionales.

    Todos los parámetros son opcionales. Si no se envía ninguno,
    devuelve todos los registros paginados.

    La búsqueda por texto (entidad, tipo_cartera) es parcial e ignora
    mayúsculas/minúsculas. Escribir "banco" encuentra "Bancolombia",
    "Banco Popular", "Banco Davivienda", etc.
    """
    # Calculamos cuántos registros saltar para la paginación
    # Página 1 → offset 0, Página 2 → offset 50, Página 3 → offset 100, etc.
    offset = (page - 1) * page_size

    try:
        # Primero contamos el total (para el campo "total" de la respuesta)
        total = _repo.count(entidad, tipo_cartera, periodo_desde, periodo_hasta)

        # Luego traemos solo los registros de esta página
        rows  = _repo.get_all(entidad, tipo_cartera, periodo_desde, periodo_hasta, offset, page_size)

    except Exception as e:
        # Si algo falla en la base de datos, respondemos con error 500
        raise HTTPException(status_code=500, detail=str(e))

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=[CarteraResponse(**row) for row in rows],
    )


@router.get("/entidades", response_model=list[str], summary="Listar entidades financieras")
def get_entidades():
    """
    Devuelve la lista completa de entidades financieras disponibles.

    Útil para saber qué valores exactos usar en el filtro ?entidad=
    o para poblar un selector en una aplicación.
    """
    try:
        return _repo.get_entidades()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tipos", response_model=list[str], summary="Listar tipos de cartera")
def get_tipos():
    """
    Devuelve la lista completa de tipos de cartera disponibles.

    Útil para saber qué valores exactos usar en el filtro ?tipo_cartera=
    """
    try:
        return _repo.get_tipos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
