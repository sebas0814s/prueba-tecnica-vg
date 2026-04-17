"""
rpa/transformer.py
------------------
Segunda etapa del pipeline ETL: TRANSFORMACIÓN.

El CSV de datos.gov.co viene con nombres de columna en mayúsculas,
fechas en formato DD/MM/YYYY y saldos con puntos y comas (formato
colombiano). Este módulo lo convierte todo al formato que necesita
la base de datos.

Este módulo NO sabe de dónde vienen los datos ni a dónde van.
Solo recibe un DataFrame sucio y devuelve uno limpio.
"""

import pandas as pd


# -----------------------------------------------------------------------
# Mapeo entre los nombres del CSV original y los nombres de la base de datos
#
# Clave   = nombre de la columna tal como viene en el CSV
# Valor   = nombre que queremos en la base de datos
# -----------------------------------------------------------------------
CSV_COLUMNS = {
    "NOMBREENTIDAD": "entidad",
    "DESCRIP_UC":    "tipo_cartera",
    "DESC_RENGLON":  "producto",
    "FECHA_CORTE":   "periodo",
    "(1) Saldo de la cartera a la fecha de corte del reporte": "saldo",
}

# Columnas que deben existir en el DataFrame después de transformar
REQUIRED_COLUMNS = list(CSV_COLUMNS.values())

# Columnas que identifican un registro de forma única (no pueden repetirse)
KEY_COLUMNS = ["entidad", "tipo_cartera", "producto", "periodo"]


class DataTransformer:
    """
    Limpia y normaliza el DataFrame crudo antes de cargarlo en PostgreSQL.

    El proceso se divide en 4 pasos pequeños, cada uno en su propio método.
    Esto hace que sea fácil entender qué está pasando y dónde buscar
    si algo falla.
    """

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Punto de entrada principal. Aplica los 4 pasos de limpieza en orden.

        Recibe: DataFrame con los datos crudos del CSV
        Retorna: DataFrame limpio y listo para insertar en la base de datos
        """
        print("[Transformer] Iniciando transformación...")

        df = self._select_and_rename(df)   # Paso 1: quedarse solo con las columnas útiles
        df = self._drop_null_keys(df)       # Paso 2: eliminar filas incompletas
        df = self._cast_types(df)           # Paso 3: convertir tipos de datos
        df = self._drop_duplicates(df)      # Paso 4: eliminar filas repetidas

        print(f"[Transformer] Registros después de transformación: {len(df)}")
        return df

    # -----------------------------------------------------------------------
    # Métodos privados — cada uno hace exactamente una cosa
    # El guión bajo al inicio (_) indica que son de uso interno
    # -----------------------------------------------------------------------

    def _select_and_rename(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Paso 1: Del CSV original (que tiene ~26 columnas) nos quedamos
        solo con las 5 que necesitamos y las renombramos al español limpio.

        Si el CSV no tiene alguna columna esperada, lanza un error claro
        en lugar de fallar silenciosamente más adelante.
        """
        # Verificamos que todas las columnas necesarias existan en el CSV
        missing = [col for col in CSV_COLUMNS.keys() if col not in df.columns]
        if missing:
            raise ValueError(f"[Transformer] Columnas no encontradas en el CSV: {missing}")

        # Seleccionamos solo las columnas del mapeo y las renombramos
        return df[list(CSV_COLUMNS.keys())].rename(columns=CSV_COLUMNS)

    def _drop_null_keys(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Paso 2: Eliminamos filas donde algún campo clave está vacío.

        Un registro sin entidad, sin tipo de cartera, sin producto o sin
        fecha no tiene sentido guardarlo — no se puede identificar.
        """
        before = len(df)
        df = df.dropna(subset=KEY_COLUMNS)
        dropped = before - len(df)

        if dropped > 0:
            print(f"[Transformer] Filas eliminadas por campos nulos: {dropped}")

        return df

    def _cast_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Paso 3: Convierte cada columna al tipo de dato correcto.

        El CSV guarda todo como texto. Aquí:
        - Las columnas de texto se limpian (eliminamos espacios extra)
        - La fecha pasa de "31/01/2015" a "2015-01" (año-mes)
        - El saldo pasa de "1.234.567,89" a 1234567.89 (número real)
        """
        # Limpiar espacios extras en los textos
        df["entidad"]      = df["entidad"].astype(str).str.strip()
        df["tipo_cartera"] = df["tipo_cartera"].astype(str).str.strip()
        df["producto"]     = df["producto"].astype(str).str.strip()

        # Convertir fecha: "31/01/2015" → "2015-01"
        # pd.to_datetime interpreta la fecha y strftime la formatea
        fechas = pd.to_datetime(df["periodo"], format="%d/%m/%Y", errors="coerce")
        df["periodo"] = fechas.dt.strftime("%Y-%m")

        # Convertir saldo: el formato colombiano usa punto como separador de miles
        # y coma como separador decimal. Ej: "1.234.567,89"
        # Primero quitamos los puntos de miles, luego reemplazamos la coma por punto
        df["saldo"] = (
            df["saldo"]
            .astype(str)
            .str.replace(".", "", regex=False)   # "1.234.567,89" → "1234567,89"
            .str.replace(",", ".", regex=False)  # "1234567,89"   → "1234567.89"
        )
        df["saldo"] = pd.to_numeric(df["saldo"], errors="coerce")  # "1234567.89" → 1234567.89

        return df

    def _drop_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Paso 4: Eliminamos filas duplicadas.

        Un duplicado es cualquier fila que tenga la misma combinación de
        entidad + tipo_cartera + producto + periodo. Nos quedamos con
        la última aparición (keep="last").
        """
        before = len(df)
        df = df.drop_duplicates(subset=KEY_COLUMNS, keep="last")
        dropped = before - len(df)

        if dropped > 0:
            print(f"[Transformer] Duplicados eliminados: {dropped}")

        return df.reset_index(drop=True)  # Reiniciamos el índice para que quede limpio
