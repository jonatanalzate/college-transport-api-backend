from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.data.database import Base
import uuid

class Vehiculo(Base):
    __tablename__ = "vehiculos"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    marca = Column(String, nullable=False)
    placa = Column(String, unique=True, index=True, nullable=False)
    modelo = Column(String, nullable=False)
    lateral = Column(String, nullable=False)
    año_de_fabricacion = Column(Integer, nullable=False)
    capacidad_pasajeros = Column(Integer, nullable=False)
    estado_operativo = Column(String, nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    empresa = relationship("Empresa", back_populates="vehiculos")