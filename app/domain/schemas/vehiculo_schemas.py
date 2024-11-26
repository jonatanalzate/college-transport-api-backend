from pydantic import BaseModel, Field
from typing import Optional

class VehiculoBase(BaseModel):
    marca: str
    placa: str
    modelo: str
    lateral: str
    año_de_fabricacion: int
    capacidad_pasajeros: int
    estado_operativo: str

class VehiculoCrear(VehiculoBase):
    pass

class Vehiculo(VehiculoBase):
    id: str
    empresa_id: Optional[int] = None

    class Config:
        from_attributes = True

class VehiculoActualizar(BaseModel):
    marca: Optional[str] = None
    placa: Optional[str] = None
    modelo: Optional[str] = None
    lateral: Optional[str] = None
    año_de_fabricacion: Optional[int] = None
    capacidad_pasajeros: Optional[int] = None
    estado_operativo: Optional[str] = None