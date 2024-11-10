from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.domain.models.conductor import Conductor as ConductorModelo
from app.domain.schemas.conductor_schemas import ConductorCrear, Conductor, ConductorActualizar
from app.data.database import get_db
from typing import List

router = APIRouter()

@router.post("/conductores/", response_model=List[Conductor], tags=["Conductores"])
def crear_conductores(conductores: List[ConductorCrear], db: Session = Depends(get_db)): 
    db_conductores = []
    for conductor in conductores:
        db_conductor = ConductorModelo(**conductor.model_dump())
        db.add(db_conductor)
        db_conductores.append(db_conductor)
    try:    
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error: Conductor duplicado.")        
    return db_conductores

@router.get("/conductores/", response_model=List[Conductor], tags=["Conductores"])
def leer_conductores(db: Session = Depends(get_db)):
    conductores = db.query(ConductorModelo).all()
    return [Conductor.model_validate(conductor.__dict__) for conductor in conductores]

@router.put("/conductores/{conductor_id}", response_model=Conductor, tags=["Conductores"])
async def modificar_conductor(conductor_id: str, conductor: Conductor, db: Session = Depends(get_db)):
    db_conductor = db.query(ConductorModelo).filter(ConductorModelo.id == conductor_id).first()
    if not db_conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado.")
    for key, value in conductor.model_dump().items():
        setattr(db_conductor, key, value)
    db.commit()
    conductor_dict = {k: getattr(db_conductor, k) for k in Conductor.model_fields.keys()}
    return Conductor.model_validate(db_conductor.__dict__)

@router.patch("/conductores/{conductor_id}", response_model=Conductor, tags=["Conductores"])
async def modificar_conductor_parcial(conductor_id: str, conductor: ConductorActualizar, db: Session = Depends(get_db)):
    db_conductor = db.query(ConductorModelo).filter(ConductorModelo.id == conductor_id).first()
    if not db_conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado.")
    
    # Solo actualizar los campos que se envían en la solicitud
    for key, value in conductor.model_dump(exclude_unset=True).items():
        if value is not None:  # Asegúrate de que el valor no sea None
            setattr(db_conductor, key, value)
    
    db.commit()
    
    # Crear un diccionario con los valores actualizados
    conductor_dict = {
        "id": db_conductor.id,
        "nombre": db_conductor.nombre,
        "cedula": db_conductor.cedula,
        "licencia": db_conductor.licencia,
        "telefono": db_conductor.telefono,
        "estado": db_conductor.estado,
    }
    
    return Conductor.model_validate(conductor_dict)

@router.get("/conductores/{conductor_placa}", response_model=Conductor, tags=["Conductores"])
async def obtener_conductor(conductor_placa: str, db: Session = Depends(get_db)):
    db_conductor = db.query(ConductorModelo).filter(ConductorModelo.placa == conductor_placa).first()
    if not db_conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado.")
    return Conductor.model_validate(db_conductor.__dict__)

@router.delete("/conductores/{conductor_id}", response_model=dict, tags=["Conductores"])
async def eliminar_conductor(conductor_id: str, db: Session = Depends(get_db)):
    db_conductor = db.query(ConductorModelo).filter(ConductorModelo.placa == conductor_id).first()
    if not db_conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado.")
    db.delete(db_conductor)
    db.commit()
    return {"detail": "Conductor eliminado exitosamente."}