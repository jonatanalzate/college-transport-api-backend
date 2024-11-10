# app/domain/schemas/vehiculo_schemas.py
from pydantic import BaseModel
from typing import Optional

class ConductorCrear(BaseModel):
    nombre: str
    cedula: str
    licencia: str
    telefono: str
    estado: int

class Conductor(BaseModel):
    id: str
    nombre: str
    cedula: str
    licencia: str
    telefono: str
    estado: str 

class ConductorActualizar(BaseModel):
    nombre: Optional[str] = None
    cedula: Optional[str] = None
    licencia: Optional[str] = None
    telefono: Optional[str] = None
    estado: Optional[str] = None