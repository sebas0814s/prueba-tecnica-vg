"""
rpa/loader.py
-------------
Tercera etapa del pipeline ETL: CARGA (Load).

Este módulo toma el DataFrame ya limpio y lo guarda en la base de datos
PostgreSQL, registro por registro.

La estrategia usada es UPSERT (mezcla de INSERT + UPDATE):
- Si el registro NO existe → lo inserta (INSERT)
- Si el registro YA existe → actualiza solo el saldo (UPDATE)

Esto hace que el RPA sea "idempotente": puedes correrlo 10 veces
y el resultado siempre será el mismo, sin duplicados.
"""

import pandas as pd
from sqlalchemy import text
from database.connection import get_session


# Nombre de la tabla en PostgreSQL donde se guardan los datos
TABLE_NAME = "cartera_financiera"

# Estas 4 columnas juntas identifican un registro de forma única.
# Si ya existe una fila con la misma combinación, se actualiza en lugar de insertar.
UNIQUE_KEYS = ["entidad", "tipo_cartera", "producto", "periodo"]


class PostgreSQLLoader:
    """
    Guarda el DataFrame en PostgreSQL usando la estrategia UPSERT.

    No sabe nada de cómo se obtuvieron o limpiaron los datos.
    Solo recibe un DataFrame listo y lo persiste en la base de datos.
    """

    def load(self, df: pd.DataFrame) -> None:
        """
        Recorre el DataFrame fila por fila y hace upsert de cada registro.

        Usa una transacción: si algo falla a mitad del proceso, se
        revierten TODOS los cambios (rollback) para no dejar datos
        a medias en la base de datos.
        """
        print(f"[Loader] Iniciando carga de {len(df)} registros...")

        session = get_session()
        try:
            inserted = 0  # Contador de registros nuevos
            updated  = 0  # Contador de registros actualizados

            for _, row in df.iterrows():
                # Convertimos cada fila del DataFrame a un diccionario
                # para pasarlo como parámetro al SQL
                result = self._upsert_row(session, row.to_dict())

                if result == "inserted":
                    inserted += 1
                else:
                    updated += 1

            # Confirmamos todos los cambios de una vez (más eficiente que
            # hacer commit después de cada fila)
            session.commit()
            print(f"[Loader] Insertados: {inserted} | Actualizados: {updated}")

        except Exception as error:
            # Si algo sale mal, revertimos todo para no dejar la BD a medias
            session.rollback()
            raise error

        finally:
            # Siempre cerramos la conexión, haya error o no
            session.close()

    def _upsert_row(self, session, row: dict) -> str:
        """
        Ejecuta la operación UPSERT para un solo registro.

        La cláusula ON CONFLICT le dice a PostgreSQL:
        "Si ya existe un registro con esta combinación de claves,
        en lugar de fallar, actualiza el saldo con el nuevo valor."

        RETURNING (xmax = 0) es un truco de PostgreSQL para saber si
        el registro fue insertado (xmax = 0 → True) o actualizado (xmax > 0 → False).
        """
        sql = text(f"""
            INSERT INTO {TABLE_NAME} (entidad, tipo_cartera, producto, periodo, saldo)
            VALUES (:entidad, :tipo_cartera, :producto, :periodo, :saldo)
            ON CONFLICT (entidad, tipo_cartera, producto, periodo)
            DO UPDATE SET saldo = EXCLUDED.saldo
            RETURNING (xmax = 0) AS was_inserted
        """)

        result = session.execute(sql, row).fetchone()

        # Si was_inserted es True → fue un INSERT nuevo
        # Si was_inserted es False → fue un UPDATE de un registro existente
        return "inserted" if result[0] else "updated"
