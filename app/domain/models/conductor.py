from sqlalchemy import Column, String
from app.data.database import Base
import uuid

class Conductor(Base):
    __tablename__ = "conductores"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String, nullable=False)
    cedula = Column(String, unique=True, index=True, nullable=False)
    licencia = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
    estado = Column(String, nullable=False)