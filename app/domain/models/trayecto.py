from sqlalchemy import Column, String, Date, Time, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.data.database import Base
from app.domain.models.ruta import Ruta
from app.domain.models.conductor import Conductor
from app.domain.models.vehiculo import Vehiculo
import uuid

class Trayecto(Base):
    __tablename__ = "trayectos"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    fecha = Column(Date, nullable=False)
    hora_salida = Column(Time, nullable=False)
    hora_llegada = Column(Time, nullable=False)
    cantidad_pasajeros = Column(Integer, nullable=False)
    kilometraje = Column(Integer, nullable=False)
    observaciones = Column(String, nullable=True)
    ruta_id = Column(String, ForeignKey("rutas.id"), nullable=True)
    conductor_id = Column(String, ForeignKey("conductores.id"), nullable=True)
    vehiculo_id = Column(String, ForeignKey("vehiculos.id"), nullable=True)
    
    # Relaciones
    ruta = relationship("Ruta", back_populates="trayectos")
    conductor = relationship("Conductor", foreign_keys=[conductor_id])
    vehiculo = relationship("Vehiculo", foreign_keys=[vehiculo_id])