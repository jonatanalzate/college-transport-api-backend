from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class Ruta(Base):
    __tablename__ = "rutas"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String, nullable=False)
    codigo = Column(String, unique=True, index=True, nullable=False)
    origen = Column(String, nullable=False)
    destino = Column(String, nullable=False)
    duracion_estimada = Column(Integer, nullable=False)