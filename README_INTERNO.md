# Prueba Técnica - Practicante TI (Vision Gerencial)

Análisis de la distribución de cartera reportada por entidades financieras colombianas.  
Fuente: [Datos Abiertos Gov](https://www.datos.gov.co/Hacienda-y-Cr-dito-P-blico/Distribuci-n-de-cartera-por-producto/rvii-eis8/about_data)

---

## Estructura del proyecto

```
prueba-tecnica-vg/
├── data/
│   └── cartera.csv          # CSV exportado de datos.gov.co
├── config/
│   └── settings.py          # Variables de entorno
├── database/
│   ├── connection.py        # Conexión SQLAlchemy a PostgreSQL
│   └── schema.sql           # DDL para crear la tabla
├── rpa/
│   ├── extractor.py         # Lee el CSV local
│   ├── transformer.py       # Limpia y normaliza los datos
│   ├── loader.py            # Carga los datos en PostgreSQL
│   └── pipeline.py          # Orquesta el ETL completo
├── api/
│   ├── main.py              # Punto de entrada FastAPI
│   ├── routes/cartera.py    # Endpoints REST
│   ├── models/cartera.py    # Schemas Pydantic
│   └── repositories/cartera_repo.py  # Queries a la BD
├── requirements.txt
└── .env.example
```

---

## Requisitos previos

- Python 3.11+
- PostgreSQL 14+

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd prueba-tecnica-vg

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
copy .env.example .env
# Editar .env con tus credenciales de PostgreSQL
```

---

## Configuración de la base de datos

```bash
# Crear la base de datos en PostgreSQL
psql -U postgres -c "CREATE DATABASE cartera_db;"

# Crear la tabla
psql -U postgres -d cartera_db -f database/schema.sql
```

---

## Ejecutar el RPA (ETL)

Coloca el archivo CSV exportado de datos.gov.co en `data/cartera.csv`, luego:

```bash
python -m rpa.pipeline
```

Esto extrae los datos del CSV, los transforma y los carga en PostgreSQL.

---

## Ejecutar la API

```bash
uvicorn api.main:app --reload
```

La documentación interactiva queda disponible en: http://127.0.0.1:8000/docs

---

## Endpoints disponibles

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/cartera` | Lista registros con filtros opcionales |
| GET | `/cartera/entidades` | Lista de entidades únicas |
| GET | `/cartera/tipos` | Lista de tipos de cartera únicos |

### Parámetros de filtro en `/cartera`

| Parámetro | Tipo | Ejemplo |
|-----------|------|---------|
| `entidad` | string | `Bancolombia` |
| `tipo_cartera` | string | `Comercial` |
| `periodo_desde` | string | `2023-01` |
| `periodo_hasta` | string | `2024-12` |
| `page` | int | `1` |
| `page_size` | int | `50` |

---

## Principios SOLID aplicados

- **S** — Responsabilidad única: cada módulo hace exactamente una cosa.
- **O** — Abierto/cerrado: el extractor recibe la ruta como parámetro, fácil de extender.
- **L** — Sustitución de Liskov: el repositorio hereda de una interfaz base intercambiable.
- **I** — Segregación de interfaces: modelos Pydantic separados por responsabilidad.
- **D** — Inversión de dependencias: la API depende de la interfaz del repositorio, no de PostgreSQL directamente.
