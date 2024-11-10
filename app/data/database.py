from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de la base de datos
DATABASE_URL = "sqlite:///./transporte.db"

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL)

# Crear una clase de sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear una clase base para los modelos
Base = declarative_base()

def get_db():
    """
    Generador que proporciona una sesión de base de datos.
    Cierra la sesión al final de la operación.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()