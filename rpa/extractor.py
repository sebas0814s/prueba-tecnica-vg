"""
rpa/extractor.py
----------------
Primera etapa del pipeline ETL: EXTRACCIÓN.

Este módulo tiene una única responsabilidad: leer el archivo CSV
y entregarlo como un DataFrame de pandas para que el siguiente paso
(transformer.py) lo procese.

Un DataFrame es básicamente una tabla en memoria, similar a una hoja
de Excel, pero que podemos manipular con código Python.
"""

import pandas as pd
from config.settings import settings


class CSVExtractor:
    """
    Lee el archivo CSV exportado de datos.gov.co y lo convierte
    en un DataFrame listo para transformar.

    Se diseñó así (recibiendo la ruta como parámetro) para que sea
    fácil cambiar la fuente de datos en el futuro sin tocar este código.
    Por ejemplo, si mañana el archivo se llama diferente, solo cambias
    el valor en el .env y listo.
    """

    def __init__(self, csv_path: str = settings.csv_path):
        # Guardamos la ruta del archivo para usarla al extraer
        self.csv_path = csv_path

    def extract(self) -> pd.DataFrame:
        """
        Lee el CSV y retorna todos los datos como un DataFrame.

        - encoding="utf-8": le dice a pandas que el archivo usa caracteres
          especiales como tildes y eñes.
        - low_memory=False: evita que pandas adivine el tipo de dato de cada
          columna, lo cual puede causar errores en archivos grandes.
        """
        print(f"[Extractor] Leyendo archivo: {self.csv_path}")

        df = pd.read_csv(self.csv_path, encoding="utf-8", low_memory=False)

        print(f"[Extractor] Registros leídos: {len(df)}")
        return df
