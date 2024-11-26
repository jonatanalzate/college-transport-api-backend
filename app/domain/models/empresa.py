from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.data.database import Base

class Empresa(Base):
    __tablename__ = "empresas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    nit = Column(String, unique=True)
    hashed_password = Column(String)
    
    # Relaciones con otros modelos
    vehiculos = relationship("Vehiculo", back_populates="empresa")
    conductores = relationship("Conductor", back_populates="empresa")
    rutas = relationship("Ruta", back_populates="empresa")
    trayectos = relationship("Trayecto", back_populates="empresa") 