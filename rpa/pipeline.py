"""
pipeline.py — Punto de entrada del RPA.

Orquesta las tres etapas del ETL:
    1. Extractor  → lee el CSV local
    2. Transformer → limpia y normaliza los datos
    3. Loader      → persiste los datos en PostgreSQL

Principio D (Inversión de dependencias): el pipeline recibe
las dependencias como parámetros, no las instancia internamente.
Esto facilita reemplazarlas o probarlas de forma independiente.

Uso:
    python -m rpa.pipeline
"""

import time
from rpa.extractor import CSVExtractor
from rpa.transformer import DataTransformer
from rpa.loader import PostgreSQLLoader


def run_pipeline(
    extractor: CSVExtractor = None,
    transformer: DataTransformer = None,
    loader: PostgreSQLLoader = None,
) -> None:
    """
    Ejecuta el pipeline ETL completo.
    Las dependencias son opcionales: si no se pasan, se usan las implementaciones por defecto.
    """
    extractor   = extractor   or CSVExtractor()
    transformer = transformer or DataTransformer()
    loader      = loader      or PostgreSQLLoader()

    print("=" * 50)
    print("  RPA - Pipeline de Cartera Financiera")
    print("=" * 50)

    start = time.time()

    raw_df       = extractor.extract()
    clean_df     = transformer.transform(raw_df)
    loader.load(clean_df)

    elapsed = round(time.time() - start, 2)
    print("=" * 50)
    print(f"  Pipeline completado en {elapsed}s")
    print("=" * 50)


if __name__ == "__main__":
    run_pipeline()
