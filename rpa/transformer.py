import pandas as pd


# Columnas del CSV original que necesitamos
CSV_COLUMNS = {
    "NOMBREENTIDAD": "entidad",
    "DESCRIP_UC":    "tipo_cartera",
    "DESC_RENGLON":  "producto",
    "FECHA_CORTE":   "periodo",
    "(1) Saldo de la cartera a la fecha de corte del reporte": "saldo",
}

REQUIRED_COLUMNS = list(CSV_COLUMNS.values())
KEY_COLUMNS      = ["entidad", "tipo_cartera", "producto", "periodo"]


class DataTransformer:
    """
    Responsabilidad única: limpiar y normalizar el DataFrame crudo
    antes de cargarlo en la base de datos.

    No sabe de dónde vienen los datos ni a dónde van; solo los transforma.
    """

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica todas las transformaciones en orden:
        1. Selecciona y renombra solo las columnas necesarias.
        2. Elimina filas con campos clave nulos.
        3. Limpia y castea tipos de datos.
        4. Convierte FECHA_CORTE (DD/MM/YYYY) al formato YYYY-MM.
        5. Elimina duplicados.
        """
        print("[Transformer] Iniciando transformación...")

        df = self._select_and_rename(df)
        df = self._drop_null_keys(df)
        df = self._cast_types(df)
        df = self._drop_duplicates(df)

        print(f"[Transformer] Registros después de transformación: {len(df)}")
        return df

    # ------------------------------------------------------------------ #
    # Métodos privados — cada uno con una sola responsabilidad            #
    # ------------------------------------------------------------------ #

    def _select_and_rename(self, df: pd.DataFrame) -> pd.DataFrame:
        """Selecciona solo las columnas necesarias y las renombra al esquema de la BD."""
        missing = [c for c in CSV_COLUMNS.keys() if c not in df.columns]
        if missing:
            raise ValueError(f"[Transformer] Columnas no encontradas en el CSV: {missing}")
        return df[list(CSV_COLUMNS.keys())].rename(columns=CSV_COLUMNS)

    def _drop_null_keys(self, df: pd.DataFrame) -> pd.DataFrame:
        """Elimina filas donde los campos clave son nulos."""
        before = len(df)
        df = df.dropna(subset=KEY_COLUMNS)
        dropped = before - len(df)
        if dropped > 0:
            print(f"[Transformer] Filas eliminadas por campos nulos: {dropped}")
        return df

    def _cast_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza tipos: texto limpio, fecha a YYYY-MM y saldo numérico."""
        df["entidad"]      = df["entidad"].astype(str).str.strip()
        df["tipo_cartera"] = df["tipo_cartera"].astype(str).str.strip()
        df["producto"]     = df["producto"].astype(str).str.strip()

        # FECHA_CORTE viene como "31/01/2015" → convertir a "2015-01"
        fechas = pd.to_datetime(df["periodo"], format="%d/%m/%Y", errors="coerce")
        df["periodo"] = fechas.dt.strftime("%Y-%m")

        # El saldo puede tener puntos como separador de miles y coma decimal
        df["saldo"] = (
            df["saldo"]
            .astype(str)
            .str.replace(".", "", regex=False)   # quitar separador de miles
            .str.replace(",", ".", regex=False)  # coma decimal → punto
        )
        df["saldo"] = pd.to_numeric(df["saldo"], errors="coerce")

        return df

    def _drop_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Elimina registros duplicados según las columnas clave."""
        before = len(df)
        df = df.drop_duplicates(subset=KEY_COLUMNS, keep="last")
        dropped = before - len(df)
        if dropped > 0:
            print(f"[Transformer] Duplicados eliminados: {dropped}")
        return df.reset_index(drop=True)
