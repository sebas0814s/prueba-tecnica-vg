from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy import text
from database.connection import get_session


# ------------------------------------------------------------------ #
# Interfaz base (Principio L y D)                                     #
# La API depende de esta abstracción, no de la implementación concreta #
# ------------------------------------------------------------------ #

class CarteraRepositoryBase(ABC):
    """Contrato que debe cumplir cualquier implementación del repositorio."""

    @abstractmethod
    def get_all(
        self,
        entidad: Optional[str],
        tipo_cartera: Optional[str],
        periodo_desde: Optional[str],
        periodo_hasta: Optional[str],
        offset: int,
        limit: int,
    ) -> list[dict]:
        pass

    @abstractmethod
    def count(
        self,
        entidad: Optional[str],
        tipo_cartera: Optional[str],
        periodo_desde: Optional[str],
        periodo_hasta: Optional[str],
    ) -> int:
        pass

    @abstractmethod
    def get_entidades(self) -> list[str]:
        pass

    @abstractmethod
    def get_tipos(self) -> list[str]:
        pass


# ------------------------------------------------------------------ #
# Implementación concreta para PostgreSQL                             #
# ------------------------------------------------------------------ #

class PostgreSQLCarteraRepository(CarteraRepositoryBase):
    """
    Responsabilidad única: ejecutar las queries SQL sobre la tabla
    cartera_financiera y retornar los resultados como diccionarios.

    No conoce FastAPI ni los modelos Pydantic; solo habla con la BD.
    """

    def get_all(
        self,
        entidad: Optional[str] = None,
        tipo_cartera: Optional[str] = None,
        periodo_desde: Optional[str] = None,
        periodo_hasta: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict]:
        """Retorna registros con filtros opcionales y paginación."""
        conditions, params = self._build_conditions(
            entidad, tipo_cartera, periodo_desde, periodo_hasta
        )
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        sql = text(f"""
            SELECT id, entidad, tipo_cartera, producto, periodo, saldo
            FROM cartera_financiera
            {where}
            ORDER BY periodo DESC, entidad
            LIMIT :limit OFFSET :offset
        """)

        params.update({"limit": limit, "offset": offset})
        return self._execute_query(sql, params)

    def count(
        self,
        entidad: Optional[str] = None,
        tipo_cartera: Optional[str] = None,
        periodo_desde: Optional[str] = None,
        periodo_hasta: Optional[str] = None,
    ) -> int:
        """Cuenta el total de registros que cumplen los filtros (para paginación)."""
        conditions, params = self._build_conditions(
            entidad, tipo_cartera, periodo_desde, periodo_hasta
        )
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        sql = text(f"SELECT COUNT(*) FROM cartera_financiera {where}")
        session = get_session()
        try:
            result = session.execute(sql, params).scalar()
            return result or 0
        finally:
            session.close()

    def get_entidades(self) -> list[str]:
        """Retorna la lista de entidades únicas ordenadas alfabéticamente."""
        sql = text("SELECT DISTINCT entidad FROM cartera_financiera ORDER BY entidad")
        rows = self._execute_query(sql, {})
        return [row["entidad"] for row in rows]

    def get_tipos(self) -> list[str]:
        """Retorna la lista de tipos de cartera únicos ordenados alfabéticamente."""
        sql = text("SELECT DISTINCT tipo_cartera FROM cartera_financiera ORDER BY tipo_cartera")
        rows = self._execute_query(sql, {})
        return [row["tipo_cartera"] for row in rows]

    # ------------------------------------------------------------------ #
    # Métodos privados de ayuda                                            #
    # ------------------------------------------------------------------ #

    def _build_conditions(
        self,
        entidad: Optional[str],
        tipo_cartera: Optional[str],
        periodo_desde: Optional[str],
        periodo_hasta: Optional[str],
    ) -> tuple[list[str], dict]:
        """Construye la cláusula WHERE y los parámetros de forma dinámica."""
        conditions = []
        params = {}

        if entidad:
            conditions.append("entidad ILIKE :entidad")
            params["entidad"] = f"%{entidad}%"

        if tipo_cartera:
            conditions.append("tipo_cartera ILIKE :tipo_cartera")
            params["tipo_cartera"] = f"%{tipo_cartera}%"

        if periodo_desde:
            conditions.append("periodo >= :periodo_desde")
            params["periodo_desde"] = periodo_desde

        if periodo_hasta:
            conditions.append("periodo <= :periodo_hasta")
            params["periodo_hasta"] = periodo_hasta

        return conditions, params

    def _execute_query(self, sql, params: dict) -> list[dict]:
        """Ejecuta una query y retorna los resultados como lista de diccionarios."""
        session = get_session()
        try:
            result = session.execute(sql, params)
            keys = result.keys()
            return [dict(zip(keys, row)) for row in result.fetchall()]
        finally:
            session.close()
