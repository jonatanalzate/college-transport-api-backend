from fastapi import FastAPI
from app.data.database import engine
from app.domain.models.vehiculo import Base as VehiculoBase
from app.domain.models.ruta import Base as RutaBase
from app.presentation.api_vehiculo import router as vehiculo_router
from app.presentation.api_ruta import router as ruta_router

# Crear todas las tablas en la base de datos
VehiculoBase.metadata.create_all(bind=engine)
RutaBase.metadata.create_all(bind=engine)

# Inicializar la aplicación FastAPI
app = FastAPI()

# Incluir los routers de los endpoints
app.include_router(vehiculo_router)
app.include_router(ruta_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
    
"""
from fastapi import FastAPI
from app.data.database import engine
from app.domain.models.vehiculo import Base
from app.domain.models.ruta import Base
from app.presentation.api_vehiculo import router  # Importa el router de api.py
from app.presentation.api_ruta import router  # Importa el router de api.py

# Crear todas las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Inicializar la aplicación FastAPI
app = FastAPI()

# Incluir el router de los endpoints
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
"""
    