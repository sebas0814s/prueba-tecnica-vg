import pandas as pd
from config.settings import settings


class CSVExtractor:
    """
    Responsabilidad única: leer el archivo CSV y retornar
    un DataFrame sin ninguna transformación.

    Principio O (Abierto/Cerrado): la ruta se inyecta como parámetro,
    por lo que es fácil cambiar la fuente sin modificar esta clase.
    """

    def __init__(self, csv_path: str = settings.csv_path):
        self.csv_path = csv_path

    def extract(self) -> pd.DataFrame:
        """
        Lee el CSV exportado de datos.gov.co y retorna
        un DataFrame con los datos crudos.
        """
        print(f"[Extractor] Leyendo archivo: {self.csv_path}")
        df = pd.read_csv(self.csv_path, encoding="utf-8", low_memory=False)
        print(f"[Extractor] Registros leídos: {len(df)}")
        return df
