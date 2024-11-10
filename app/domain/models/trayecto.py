from sqlalchemy import Column, String, Integer, Date, Time
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class Trayecto(Base):
    __tablename__ = "trayectos"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(Date, nullable=False)
    hora_salida = Column(Time, nullable=False)
    hora_llegada = Column(Time, nullable=False)
    cantidad_pasajeros = Column(Integer, nullable=False)
    kilometraje = Column(Integer, nullable=False)
    observaciones = Column(String, nullable=True)