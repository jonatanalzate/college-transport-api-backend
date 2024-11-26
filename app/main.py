from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.data.database import engine
from app.domain.models.vehiculo import Base as VehiculoBase
from app.domain.models.ruta import Base as RutaBase
from app.domain.models.conductor import Base as ConductorBase
from app.domain.models.trayecto import Base as TrayectoBase
from app.domain.models.empresa import Base as EmpresaBase
from app.domain.models.usuario import Base as UsuarioBase
from app.presentation.api_vehiculo import router as vehiculo_router
from app.presentation.api_ruta import router as ruta_router
from app.presentation.api_conductor import router as conductor_router
from app.presentation.api_trayecto import router as trayecto_router
from app.presentation.api_auth import auth_router, usuarios_router

# Crear todas las tablas en la base de datos
VehiculoBase.metadata.create_all(bind=engine)
RutaBase.metadata.create_all(bind=engine)
ConductorBase.metadata.create_all(bind=engine)
TrayectoBase.metadata.create_all(bind=engine)
EmpresaBase.metadata.create_all(bind=engine)
UsuarioBase.metadata.create_all(bind=engine)

# Inicializar la aplicación FastAPI
app = FastAPI(description="API para el transporte publico de Manizales")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.20.75:3000",  # Añadir la IP local
]

# Se agrega el middleware CORS en el backend para permitir las peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers de los endpoints
app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(vehiculo_router)
app.include_router(ruta_router)
app.include_router(conductor_router)
app.include_router(trayecto_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
