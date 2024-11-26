from pydantic import BaseModel, Field
from typing import Optional

class ConductorBase(BaseModel):
    nombre: str
    cedula: str
    licencia: str
    telefono: str
    estado: str

class ConductorCrear(ConductorBase):
    pass

class Conductor(ConductorBase):
    id: str
    empresa_id: Optional[int] = None

    class Config:
        from_attributes = True

class ConductorActualizar(BaseModel):
    nombre: Optional[str] = None
    cedula: Optional[str] = None
    licencia: Optional[str] = None
    telefono: Optional[str] = None
    estado: Optional[str] = None