from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import re

Base = declarative_base()

def sanitize_db_name(name: str) -> str:
    """Convierte el email en un nombre válido para la base de datos"""
    # Extrae el nombre antes del @
    name = name.split('@')[0]
    # Elimina caracteres especiales y espacios
    name = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
    return name

def get_db_url(empresa_email=None):
    if empresa_email:
        db_name = sanitize_db_name(empresa_email)
        return f"sqlite:///{db_name}.db"
    return "sqlite:///main.db"  # Base de datos principal para autenticación

# Engine principal para autenticación
engine = create_engine(get_db_url(), connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_empresa_engine(empresa_email: str):
    """Crear un engine específico para cada empresa"""
    db_url = get_db_url(empresa_email)
    return create_engine(db_url, connect_args={"check_same_thread": False})

def get_empresa_session(empresa_email: str):
    """Obtener una sesión específica para una empresa"""
    engine = get_empresa_engine(empresa_email)
    SessionEmpresa = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionEmpresa()

def get_db():
    """Obtener sesión de la base de datos principal"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_for_empresa(empresa_email: str):
    """Obtener sesión de la base de datos de una empresa específica"""
    db = get_empresa_session(empresa_email)
    try:
        yield db
    finally:
        db.close()

def init_empresa_db(empresa_email: str):
    """Inicializar la base de datos para una nueva empresa"""
    engine = get_empresa_engine(empresa_email)
    Base.metadata.create_all(bind=engine)