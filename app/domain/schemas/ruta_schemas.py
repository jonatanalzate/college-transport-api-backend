# app/domain/schemas/vehiculo_schemas.py
from pydantic import BaseModel
from typing import Optional

class RutaCrear(BaseModel):
    nombre: str
    codigo: str
    origen: str
    destino: str
    duracion_estimada: int

class Ruta(BaseModel):
    id: str
    nombre: str
    codigo: str
    origen: str
    destino: str
    duracion_estimada: int

class RutaActualizar(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    origen: Optional[str] = None
    destino: Optional[str] = None
    duracion_estimada: Optional[int] = None