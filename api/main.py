from fastapi import FastAPI
from api.routes.cartera import router as cartera_router

app = FastAPI(
    title="API de Cartera Financiera",
    description=(
        "Consume datos de distribución de cartera reportados por entidades financieras "
        "colombianas. Fuente: Datos Abiertos Gov (datos.gov.co)."
    ),
    version="1.0.0",
    contact={
        "name": "Vision Gerencial - Prueba Técnica",
    },
)

# Registro de routers
app.include_router(cartera_router)


@app.get("/", tags=["Health"])
def health_check():
    """Verifica que la API esté en funcionamiento."""
    return {"status": "ok", "message": "API de Cartera Financiera activa"}
