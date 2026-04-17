"""
rpa/pipeline.py
---------------
Punto de entrada del RPA. Orquesta las tres etapas del proceso ETL:

    Extractor  →  Transformer  →  Loader
    (leer CSV)    (limpiar)        (guardar en BD)

Este archivo actúa como el "director de orquesta": no hace el trabajo
él mismo, sino que coordina a los módulos especializados en el orden correcto.

Para correrlo desde la terminal:
    python -m rpa.pipeline

Diseño: las dependencias (extractor, transformer, loader) se reciben como
parámetros en lugar de instanciarse internamente. Esto permite reemplazarlas
fácilmente, por ejemplo en pruebas unitarias, sin modificar este archivo.
"""

import time
from rpa.extractor   import CSVExtractor
from rpa.transformer import DataTransformer
from rpa.loader      import PostgreSQLLoader


def run_pipeline(
    extractor:   CSVExtractor   = None,
    transformer: DataTransformer = None,
    loader:      PostgreSQLLoader = None,
) -> None:
    """
    Ejecuta el pipeline ETL completo de principio a fin.

    Parámetros opcionales:
        extractor   — objeto que sabe leer los datos
        transformer — objeto que sabe limpiarlos
        loader      — objeto que sabe guardarlos en PostgreSQL

    Si no se pasan, se usan las implementaciones por defecto.
    """
    # Usamos los módulos por defecto si no se pasaron otros
    extractor   = extractor   or CSVExtractor()
    transformer = transformer or DataTransformer()
    loader      = loader      or PostgreSQLLoader()

    print("=" * 50)
    print("  RPA - Pipeline de Cartera Financiera")
    print("=" * 50)

    start = time.time()  # Marcamos el tiempo de inicio para medir duración

    # --- Etapa 1: Extracción ---
    # Lee el CSV y lo convierte en un DataFrame (tabla en memoria)
    raw_df = extractor.extract()

    # --- Etapa 2: Transformación ---
    # Limpia, normaliza y da el formato correcto a los datos
    clean_df = transformer.transform(raw_df)

    # --- Etapa 3: Carga ---
    # Inserta o actualiza los registros en PostgreSQL
    loader.load(clean_df)

    elapsed = round(time.time() - start, 2)  # Calculamos cuánto tardó en total

    print("=" * 50)
    print(f"  Pipeline completado en {elapsed}s")
    print("=" * 50)


# Este bloque solo se ejecuta cuando corremos el archivo directamente.
# Si otro módulo importa este archivo, el pipeline NO se ejecuta automáticamente.
if __name__ == "__main__":
    run_pipeline()
