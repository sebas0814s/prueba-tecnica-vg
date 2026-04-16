import pandas as pd
from sqlalchemy import text
from database.connection import get_session


TABLE_NAME = "cartera_financiera"

# Columnas de negocio que identifican un registro único
UNIQUE_KEYS = ["entidad", "tipo_cartera", "producto", "periodo"]


class PostgreSQLLoader:
    """
    Responsabilidad única: persistir el DataFrame transformado
    en la base de datos PostgreSQL.

    Usa upsert (INSERT ... ON CONFLICT DO UPDATE) para que el RPA
    sea idempotente: se puede ejecutar múltiples veces sin duplicar datos.
    """

    def load(self, df: pd.DataFrame) -> None:
        """Carga todos los registros del DataFrame usando upsert."""
        print(f"[Loader] Iniciando carga de {len(df)} registros...")

        session = get_session()
        try:
            inserted = 0
            updated = 0

            for _, row in df.iterrows():
                result = self._upsert_row(session, row.to_dict())
                if result == "inserted":
                    inserted += 1
                else:
                    updated += 1

            session.commit()
            print(f"[Loader] Insertados: {inserted} | Actualizados: {updated}")
        except Exception as error:
            session.rollback()
            raise error
        finally:
            session.close()

    def _upsert_row(self, session, row: dict) -> str:
        """
        Ejecuta un INSERT con ON CONFLICT DO UPDATE para un solo registro.
        Retorna 'inserted' o 'updated' según lo que ocurrió.
        """
        sql = text(f"""
            INSERT INTO {TABLE_NAME} (entidad, tipo_cartera, producto, periodo, saldo)
            VALUES (:entidad, :tipo_cartera, :producto, :periodo, :saldo)
            ON CONFLICT (entidad, tipo_cartera, producto, periodo)
            DO UPDATE SET saldo = EXCLUDED.saldo
            RETURNING (xmax = 0) AS was_inserted
        """)

        result = session.execute(sql, row).fetchone()
        return "inserted" if result[0] else "updated"
