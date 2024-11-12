from pydantic import BaseModel
from typing import Optional
from datetime import date, time
from app.domain.schemas.ruta_schemas import Ruta
from app.domain.schemas.conductor_schemas import Conductor
from app.domain.schemas.vehiculo_schemas import Vehiculo

class TrayectoBase(BaseModel):
    fecha: date
    hora_salida: time
    hora_llegada: time
    cantidad_pasajeros: int
    kilometraje: int
    observaciones: Optional[str] = None
    ruta_id: Optional[str] = None
    conductor_id: Optional[str] = None
    vehiculo_id: Optional[str] = None

class TrayectoCrear(TrayectoBase):
    pass

class Trayecto(TrayectoBase):
    id: str
    ruta: Optional[Ruta] = None
    conductor: Optional[Conductor] = None
    vehiculo: Optional[Vehiculo] = None

    class Config:
        from_attributes = True

class TrayectoActualizar(BaseModel):
    fecha: Optional[date] = None
    hora_salida: Optional[time] = None
    hora_llegada: Optional[time] = None
    cantidad_pasajeros: Optional[int] = None
    kilometraje: Optional[int] = None
    observaciones: Optional[str] = None
    ruta_id: Optional[str] = None
    conductor_id: Optional[str] = None
    vehiculo_id: Optional[str] = None