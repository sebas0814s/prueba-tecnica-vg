"""
api/repositories/cartera_repo.py
---------------------------------
Este módulo se encarga de hablar con la base de datos.

El patrón "Repositorio" separa las consultas SQL del resto de la lógica.
Así, si mañana cambiamos de PostgreSQL a MySQL u otro motor, solo
modificamos este archivo — los endpoints y los modelos no se tocan.

Estructura:
    CarteraRepositoryBase         → "contrato" abstracto (qué métodos debe tener)
    PostgreSQLCarteraRepository   → implementación concreta para PostgreSQL

Tener una clase base abstracta permite que la API dependa del "contrato"
y no de la implementación específica (principio D de SOLID).
"""

from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy import text
from database.connection import get_session


# ==========================================================================
# CLASE BASE — Define el "contrato" que cualquier repositorio debe cumplir
# ==========================================================================

class CarteraRepositoryBase(ABC):
    """
    Clase abstracta que define qué métodos debe tener cualquier repositorio
    de cartera, sin importar con qué base de datos trabaje.

    'abstractmethod' significa que las subclases ESTÁN OBLIGADAS a implementar
    estos métodos. Si no lo hacen, Python lanza un error al instanciarlas.
    """

    @abstractmethod
    def get_all(self, entidad, tipo_cartera, periodo_desde, periodo_hasta, offset, limit) -> list[dict]:
        """Devuelve una lista de registros aplicando filtros y paginación."""
        pass

    @abstractmethod
    def count(self, entidad, tipo_cartera, periodo_desde, periodo_hasta) -> int:
        """Cuenta cuántos registros coinciden con los filtros (para la paginación)."""
        pass

    @abstractmethod
    def get_entidades(self) -> list[str]:
        """Devuelve la lista de todas las entidades financieras únicas."""
        pass

    @abstractmethod
    def get_tipos(self) -> list[str]:
        """Devuelve la lista de todos los tipos de cartera únicos."""
        pass


# ==========================================================================
# IMPLEMENTACIÓN CONCRETA — Habla específicamente con PostgreSQL
# ==========================================================================

class PostgreSQLCarteraRepository(CarteraRepositoryBase):
    """
    Implementación del repositorio para PostgreSQL.

    Cada método abre una sesión, ejecuta su query y cierra la sesión.
    No sabe nada de FastAPI ni de Pydantic — solo habla con la base de datos.
    """

    def get_all(
        self,
        entidad:       Optional[str] = None,
        tipo_cartera:  Optional[str] = None,
        periodo_desde: Optional[str] = None,
        periodo_hasta: Optional[str] = None,
        offset:        int = 0,
        limit:         int = 50,
    ) -> list[dict]:
        """
        Consulta registros con filtros opcionales y paginación.

        - offset: cuántos registros saltar (para la paginación)
        - limit:  cuántos registros devolver como máximo
        """
        # Construimos dinámicamente los filtros WHERE según lo que se haya enviado
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
        entidad:       Optional[str] = None,
        tipo_cartera:  Optional[str] = None,
        periodo_desde: Optional[str] = None,
        periodo_hasta: Optional[str] = None,
    ) -> int:
        """
        Cuenta el total de registros que coinciden con los filtros.

        Se usa para mostrar el campo 'total' en la respuesta paginada,
        para que el cliente sepa cuántas páginas hay en total.
        """
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
        """
        Devuelve la lista de entidades financieras sin repetir.

        DISTINCT le dice a PostgreSQL que no repita valores iguales.
        """
        sql = text("SELECT DISTINCT entidad FROM cartera_financiera ORDER BY entidad")
        rows = self._execute_query(sql, {})
        return [row["entidad"] for row in rows]

    def get_tipos(self) -> list[str]:
        """Devuelve la lista de tipos de cartera sin repetir."""
        sql = text("SELECT DISTINCT tipo_cartera FROM cartera_financiera ORDER BY tipo_cartera")
        rows = self._execute_query(sql, {})
        return [row["tipo_cartera"] for row in rows]

    # -----------------------------------------------------------------------
    # Métodos privados de ayuda
    # -----------------------------------------------------------------------

    def _build_conditions(
        self,
        entidad:       Optional[str],
        tipo_cartera:  Optional[str],
        periodo_desde: Optional[str],
        periodo_hasta: Optional[str],
    ) -> tuple[list[str], dict]:
        """
        Construye la cláusula WHERE de forma dinámica según los filtros recibidos.

        Solo agrega una condición si el filtro tiene valor (no es None).
        ILIKE hace una búsqueda que ignora mayúsculas/minúsculas.
        Los % alrededor del valor permiten buscar coincidencias parciales.

        Ejemplo: entidad="banco" encontraría "Bancolombia", "Banco Popular", etc.
        """
        conditions = []
        params     = {}

        if entidad:
            conditions.append("entidad ILIKE :entidad")
            params["entidad"] = f"%{entidad}%"  # % = "cualquier cosa antes/después"

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
        """
        Ejecuta cualquier query y convierte los resultados a una lista de diccionarios.

        Convertir a diccionarios hace que sea fácil crear objetos Pydantic después,
        ya que Pydantic puede leer valores directamente de un dict.
        """
        session = get_session()
        try:
            result = session.execute(sql, params)
            keys   = result.keys()  # Nombres de las columnas del resultado
            return [dict(zip(keys, row)) for row in result.fetchall()]
        finally:
            session.close()
