# 📊 Análisis de Cartera Financiera Colombiana

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791?logo=postgresql&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.2-150458?logo=pandas&logoColor=white)
![License](https://img.shields.io/badge/licencia-MIT-green)

> Pipeline ETL + API REST para extraer, almacenar y consultar la distribución de cartera
> reportada por las entidades financieras de Colombia.
> Fuente oficial: [Datos Abiertos Gov — datos.gov.co](https://www.datos.gov.co/Hacienda-y-Cr-dito-P-blico/Distribuci-n-de-cartera-por-producto/rvii-eis8/about_data)

---

## ¿Qué hace este proyecto?

Las entidades financieras colombianas reportan periódicamente el estado de su cartera al gobierno. Esa información es pública, pero está en bruto — miles de filas en un CSV sin ningún orden útil para tomar decisiones.

Este proyecto resuelve eso en tres pasos:

1. **RPA (Python)** — Lee el archivo, lo limpia y lo carga automáticamente en una base de datos PostgreSQL.
2. **API REST (FastAPI)** — Expone los datos para que cualquier sistema los pueda consumir, filtrando por entidad, tipo de cartera y período de tiempo.
3. **Tablero (Power BI)** — Visualiza tendencias, compara entidades y analiza la distribución de productos.

---

## 🗂️ Estructura del proyecto

```
prueba-tecnica-vg/
│
├── config/
│   └── settings.py           # Variables de entorno centralizadas
│
├── database/
│   ├── connection.py         # Motor de conexión SQLAlchemy
│   └── schema.sql            # Creación de tabla e índices
│
├── rpa/
│   ├── extractor.py          # Lee el CSV → DataFrame
│   ├── transformer.py        # Limpia y normaliza los datos
│   ├── loader.py             # Inserta en PostgreSQL (upsert)
│   └── pipeline.py           # Orquesta el proceso completo
│
├── api/
│   ├── main.py               # Aplicación FastAPI
│   ├── models/cartera.py     # Schemas de entrada y respuesta
│   ├── repositories/         # Queries SQL desacopladas
│   └── routes/cartera.py     # Endpoints REST
│
├── data/                     # CSV exportado de datos.gov.co
├── requirements.txt
└── .env.example
```

---

## 🔄 Flujo de datos

```
CSV (datos.gov.co)
      │
      ▼
  Extractor ──► Transformer ──► Loader
                                   │
                                   ▼
                            PostgreSQL DB
                                   │
                                   ▼
                            FastAPI REST API
                                   │
                                   ▼
                         Power BI / cualquier cliente
```

---

## ⚙️ Instalación y uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/sebas0814s/prueba-tecnica-vg.git
cd prueba-tecnica-vg
```

### 2. Entorno virtual y dependencias

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / Mac

pip install -r requirements.txt
```

### 3. Variables de entorno

```bash
copy .env.example .env
# Edita .env con tus credenciales de PostgreSQL
```

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cartera_db
DB_USER=postgres
DB_PASSWORD=tu_password
CSV_PATH=data/tu_archivo.csv
```

### 4. Base de datos

```bash
psql -U postgres -c "CREATE DATABASE cartera_db;"
psql -U postgres -d cartera_db -f database/schema.sql
```

### 5. Ejecutar el RPA

```bash
python -m rpa.pipeline
```

```
==================================================
  RPA - Pipeline de Cartera Financiera
==================================================
[Extractor] Leyendo archivo: data/cartera.csv
[Extractor] Registros leídos: 106905
[Transformer] Iniciando transformación...
[Transformer] Registros después de transformación: 106905
[Loader] Iniciando carga de 106905 registros...
[Loader] Insertados: 106905 | Actualizados: 0
==================================================
  Pipeline completado en 41.46s
==================================================
```

### 6. Levantar la API

```bash
uvicorn api.main:app --reload
```

Documentación interactiva disponible en: **http://127.0.0.1:8000/docs**

---

## 🚀 Endpoints de la API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/cartera` | Consulta registros con filtros y paginación |
| `GET` | `/cartera/entidades` | Lista todas las entidades financieras |
| `GET` | `/cartera/tipos` | Lista todos los tipos de cartera |

### Ejemplo de consulta

```bash
GET /cartera?entidad=Bancolombia&tipo_cartera=CONSUMO&periodo_desde=2023-01&periodo_hasta=2024-12
```

```json
{
  "total": 284,
  "page": 1,
  "page_size": 50,
  "data": [
    {
      "id": 1042,
      "entidad": "Bancolombia",
      "tipo_cartera": "CREDITOS DE CONSUMO PARA EMPLEADOS",
      "producto": "CREDITOS DE CONSUMO PARA EMPLEADOS TOTAL",
      "periodo": "2023-01",
      "saldo": 487392847291.50
    }
  ]
}
```

---

## 🏗️ Principios SOLID aplicados

| Principio | Aplicación en el código |
|-----------|------------------------|
| **S** — Responsabilidad única | `extractor`, `transformer` y `loader` hacen exactamente una cosa cada uno |
| **O** — Abierto/cerrado | El extractor recibe la ruta como parámetro — fácil cambiar la fuente sin tocar la clase |
| **L** — Sustitución de Liskov | El repositorio implementa una interfaz base intercambiable |
| **I** — Segregación de interfaces | Modelos Pydantic separados para filtros y para respuestas |
| **D** — Inversión de dependencias | La API depende de la abstracción del repositorio, no de PostgreSQL directamente |

---

## 🛠️ Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Lenguaje | Python 3.11 |
| ETL / RPA | pandas |
| API | FastAPI + Uvicorn |
| ORM / DB | SQLAlchemy + psycopg2 |
| Base de datos | PostgreSQL 17 |
| Validación | Pydantic v2 |
| Configuración | pydantic-settings + python-dotenv |
| Análisis | Power BI Desktop |

---

## 📄 Licencia

MIT — libre para usar, modificar y distribuir.
