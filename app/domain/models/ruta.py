from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.data.database import Base
import uuid

class Ruta(Base):
    __tablename__ = "rutas"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String, nullable=False)
    codigo = Column(String, unique=True, index=True, nullable=False)
    origen = Column(String, nullable=False)
    destino = Column(String, nullable=False)
    duracion_estimada = Column(Integer, nullable=False)
    trayectos = relationship("Trayecto", back_populates="ruta")