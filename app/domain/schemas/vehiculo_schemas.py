from pydantic import BaseModel
from typing import Optional

class VehiculoCrear(BaseModel):
    marca: str
    placa: str
    modelo: str
    lateral: str
    año_de_fabricacion: int
    capacidad_pasajeros: int
    estado_operativo: str

class Vehiculo(BaseModel):
    id: str
    marca: str
    placa: str
    modelo: str
    lateral: str
    año_de_fabricacion: int
    capacidad_pasajeros: int
    estado_operativo: str

class VehiculoActualizar(BaseModel):
    marca: Optional[str] = None
    placa: Optional[str] = None
    modelo: Optional[str] = None
    lateral: Optional[str] = None
    año_de_fabricacion: Optional[int] = None
    capacidad_pasajeros: Optional[int] = None
    estado_operativo: Optional[str] = None