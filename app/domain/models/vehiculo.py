from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class Vehiculo(Base):
    __tablename__ = "vehiculos"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    marca = Column(String, index=True)
    placa = Column(String, unique=True, index=True)
    modelo = Column(String)
    lateral = Column(String)
    año_de_fabricación = Column(Integer)
    capacidad_pasajeros = Column(Integer)
    estado_operativo = Column(String)