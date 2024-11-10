from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.domain.models.trayecto import Trayecto as TrayectoModelo
from app.domain.schemas.trayecto_schemas import TrayectoCrear, Trayecto, TrayectoActualizar
from app.data.database import get_db
from typing import List

router = APIRouter()

@router.post("/trayectos/", response_model=List[Trayecto], tags=["Trayectos"])
def crear_trayectos(trayectos: List[TrayectoCrear], db: Session = Depends(get_db)): 
    db_trayectos = []
    for trayecto in trayectos:
        db_Trayecto = TrayectoModelo(**trayecto.model_dump())
        db.add(db_trayectos)
        db_trayectos.append(db_trayectos)
    try:    
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error: Trayecto duplicado.")        
    return db_trayectos

@router.get("/trayectos/", response_model=List[Trayecto], tags=["Trayectos"])
def leer_trayectos(db: Session = Depends(get_db)):
    trayectos = db.query(TrayectoModelo).all()
    return [Trayecto.model_validate(trayecto.__dict__) for trayecto in trayectos]

@router.put("/trayecto/{trayecto_id}", response_model=Trayecto, tags=["Trayectos"])
async def modificar_trayecto(trayecto_id: str, trayecto: Trayecto, db: Session = Depends(get_db)):
    db_trayecto = db.query(TrayectoModelo).filter(TrayectoModelo.id == trayecto_id).first()
    if not db_trayecto:
        raise HTTPException(status_code=404, detail="Trayecto no encontrado.")
    for key, value in trayecto.model_dump().items():
        setattr(db_trayecto, key, value)
    db.commit()
    trayecto_dict = {k: getattr(db_trayecto, k) for k in Trayecto.model_fields.keys()}
    return Trayecto.model_validate(db_trayecto.__dict__)

@router.patch("/trayecto/{trayecto_id}", response_model=Trayecto, tags=["Trayectos"])
async def modificar_trayecto_parcial(trayecto_id: str, trayecto: TrayectoActualizar, db: Session = Depends(get_db)):
    db_trayecto = db.query(TrayectoModelo).filter(TrayectoModelo.id == trayecto_id).first()
    if not db_trayecto:
        raise HTTPException(status_code=404, detail="Trayecto no encontrado.")
    
    # Solo actualizar los campos que se envían en la solicitud
    for key, value in trayecto.model_dump(exclude_unset=True).items():
        if value is not None:  # Asegúrate de que el valor no sea None
            setattr(db_trayecto, key, value)
    
    db.commit()
    
    # Crear un diccionario con los valores actualizados
    trayecto_dict = {
        "id": db_trayecto.id,
        "fecha": db_trayecto.fecha,
        "hora_salida": db_trayecto.hora_salida,
        "hora_llegada": db_trayecto.hora_llegada,
        "cantidad_pasajeros": db_trayecto.cantidad_pasajeros,
        "kilometraje": db_trayecto.kilometraje,
        "observaciones": db_trayecto.observaciones,
    }
    
    return Trayecto.model_validate(trayecto_dict)

@router.get("/trayecto/{trayecto_id}", response_model=Trayecto, tags=["Trayectos"])
async def obtener_trayecto(trayecto_id: str, db: Session = Depends(get_db)):
    db_trayecto = db.query(TrayectoModelo).filter(TrayectoModelo.placa == trayecto_id).first()
    if not db_trayecto:
        raise HTTPException(status_code=404, detail="Trayecto no encontrado.")
    return Trayecto.model_validate(db_trayecto.__dict__)

@router.delete("/trayecto/{trayecto_id}", response_model=dict, tags=["Trayectos"])
async def eliminar_trayecto(trayecto_id: str, db: Session = Depends(get_db)):
    db_trayecto = db.query(TrayectoModelo).filter(TrayectoModelo.placa == trayecto_id).first()
    if not db_trayecto:
        raise HTTPException(status_code=404, detail="Trayecto no encontrado.")
    db.delete(db_trayecto)
    db.commit()
    return {"detail": "Trayecto eliminado exitosamente."}