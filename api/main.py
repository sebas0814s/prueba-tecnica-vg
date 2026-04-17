"""
api/main.py
-----------
Punto de entrada de la API. Aquí se crea la aplicación FastAPI
y se registran todas las rutas.

Para iniciar el servidor:
    uvicorn api.main:app --reload

    - api.main  → el archivo (api/main.py)
    - app       → el objeto FastAPI definido aquí abajo
    - --reload  → reinicia el servidor automáticamente al guardar cambios

Una vez iniciado, la documentación interactiva está disponible en:
    http://127.0.0.1:8000/docs   (Swagger UI)
    http://127.0.0.1:8000/redoc  (ReDoc — versión alternativa)
"""

from fastapi import FastAPI
from api.routes.cartera import router as cartera_router


# Creamos la aplicación con metadata que aparece en la documentación /docs
app = FastAPI(
    title="API de Cartera Financiera",
    description=(
        "Consume datos de distribución de cartera reportados por entidades financieras "
        "colombianas. Fuente original: Datos Abiertos Gov (datos.gov.co)."
    ),
    version="1.0.0",
    contact={
        "name": "Vision Gerencial — Prueba Técnica",
    },
)

# Registramos el router de cartera.
# Todos los endpoints definidos en api/routes/cartera.py quedan disponibles
# automáticamente bajo el prefijo /cartera.
app.include_router(cartera_router)


@app.get("/", tags=["Health"])
def health_check():
    """
    Endpoint de verificación de estado.

    Sirve para confirmar que la API está corriendo correctamente.
    Útil para monitoreo y herramientas de deployment.
    """
    return {"status": "ok", "message": "API de Cartera Financiera activa"}
