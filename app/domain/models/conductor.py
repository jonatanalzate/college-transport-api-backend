from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
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
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    empresa = relationship("Empresa", back_populates="conductores")