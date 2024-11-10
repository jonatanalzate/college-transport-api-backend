# app/domain/schemas/vehiculo_schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import date, time

class TrayectoCrear(BaseModel):
    fecha: date
    hora_salida: time
    hora_llegada: time
    cantidad_pasajeros: int
    kilometraje: int
    observaciones: Optional[str] = None

class Trayecto(BaseModel):
    id: str
    fecha: date
    hora_salida: time
    hora_llegada: time
    cantidad_pasajeros: int
    kilometraje: int
    observaciones: Optional[str] = None

class TrayectoActualizar(BaseModel):
    fecha: Optional[date] = None
    hora_salida: Optional[time] = None
    hora_llegada: Optional[time] = None
    cantidad_pasajeros: Optional[str] = None
    kilometraje: Optional[int] = None
    observaciones: Optional[str] = None