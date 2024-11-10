from fastapi import FastAPI
from app.data.database import engine
from app.domain.models.vehiculo import Base
from app.presentation.api_vehiculo import router  # Importa el router de api.py

# Crear todas las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Inicializar la aplicación FastAPI
app = FastAPI()

# Incluir el router de los endpoints
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)