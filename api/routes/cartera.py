from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from api.models.cartera import CarteraResponse, PaginatedResponse
from api.repositories.cartera_repo import PostgreSQLCarteraRepository

router = APIRouter(prefix="/cartera", tags=["Cartera Financiera"])

# Principio D: el router depende de la abstracción CarteraRepositoryBase,
# no de la implementación concreta. Se puede cambiar a otro motor de BD
# simplemente pasando una instancia diferente.
_repo = PostgreSQLCarteraRepository()


@router.get("", response_model=PaginatedResponse, summary="Consultar registros de cartera")
def get_cartera(
    entidad: Optional[str] = Query(None, description="Nombre parcial o exacto de la entidad financiera"),
    tipo_cartera: Optional[str] = Query(None, description="Tipo de cartera (ej: Comercial, Consumo)"),
    periodo_desde: Optional[str] = Query(None, description="Periodo inicial en formato YYYY-MM"),
    periodo_hasta: Optional[str] = Query(None, description="Periodo final en formato YYYY-MM"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=500, description="Registros por página"),
):
    """
    Retorna registros de distribución de cartera con filtros opcionales.

    - Filtra por **entidad** y/o **tipo_cartera** con búsqueda parcial (ILIKE).
    - Filtra por rango de **periodo** (formato YYYY-MM).
    - Soporta **paginación** con `page` y `page_size`.
    """
    offset = (page - 1) * page_size

    try:
        total = _repo.count(entidad, tipo_cartera, periodo_desde, periodo_hasta)
        rows  = _repo.get_all(entidad, tipo_cartera, periodo_desde, periodo_hasta, offset, page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=[CarteraResponse(**row) for row in rows],
    )


@router.get("/entidades", response_model=list[str], summary="Listar entidades financieras")
def get_entidades():
    """Retorna la lista de todas las entidades financieras disponibles en la base de datos."""
    try:
        return _repo.get_entidades()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tipos", response_model=list[str], summary="Listar tipos de cartera")
def get_tipos():
    """Retorna la lista de todos los tipos de cartera disponibles en la base de datos."""
    try:
        return _repo.get_tipos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
