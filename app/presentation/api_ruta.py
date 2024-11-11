from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.domain.models.ruta import Ruta as RutaModelo
from app.domain.schemas.ruta_schemas import RutaCrear, Ruta, RutaActualizar
from app.data.database import get_db
from typing import List

router = APIRouter()

@router.post("/rutas/", response_model=List[Ruta], tags=["Rutas"])
def crear_rutas(rutas: List[RutaCrear], db: Session = Depends(get_db)): 
    db_rutas = []
    for ruta in rutas:
        db_ruta = RutaModelo(**ruta.model_dump())
        db.add(db_ruta)
        db_rutas.append(db_ruta)
    try:    
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error: Ruta duplicada.")        
    return db_rutas

@router.get("/rutas/", response_model=List[Ruta], tags=["Rutas"])
def leer_rutas(db: Session = Depends(get_db)):
    rutas = db.query(RutaModelo).all()
    return [Ruta.model_validate(ruta.__dict__) for ruta in rutas]

@router.put("/ruta/{ruta_id}", response_model=Ruta, tags=["Rutas"])
async def modificar_ruta(ruta_id: str, ruta: Ruta, db: Session = Depends(get_db)):
    db_ruta = db.query(RutaModelo).filter(RutaModelo.id == ruta_id).first()
    if not db_ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada.")
    for key, value in ruta.model_dump().items():
        setattr(db_ruta, key, value)
    db.commit()
    ruta_dict = {k: getattr(db_ruta, k) for k in Ruta.model_fields.keys()}
    return Ruta.model_validate(db_ruta.__dict__)

@router.patch("/ruta/{ruta_id}", response_model=Ruta, tags=["Rutas"])
async def modificar_ruta_parcial(ruta_id: str, ruta: RutaActualizar, db: Session = Depends(get_db)):
    db_ruta = db.query(RutaModelo).filter(RutaModelo.id == ruta_id).first()
    if not db_ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada.")
    
    # Solo actualizar los campos que se envían en la solicitud
    for key, value in ruta.model_dump(exclude_unset=True).items():
        if value is not None:  # Asegúrate de que el valor no sea None
            setattr(db_ruta, key, value)
    
    db.commit()
    
    # Crear un diccionario con los valores actualizados
    ruta_dict = {
        "id": db_ruta.id,
        "nombre": db_ruta.nombre,
        "codigo": db_ruta.codigo,
        "origen": db_ruta.origen,
        "destino": db_ruta.destino,
        "duracion_estimada": db_ruta.duracion_estimada,
    }
    
    return Ruta.model_validate(ruta_dict)

@router.get("/ruta/{ruta_id}", response_model=Ruta, tags=["Rutas"])
async def obtener_ruta(ruta_id: str, db: Session = Depends(get_db)):
    db_ruta = db.query(RutaModelo).filter(RutaModelo.id == ruta_id).first()
    if not db_ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrado.")
    return Ruta.model_validate(db_ruta.__dict__)

@router.delete("/ruta/{ruta_id}", response_model=dict, tags=["Rutas"])
async def eliminar_ruta(ruta_id: str, db: Session = Depends(get_db)):
    db_ruta = db.query(RutaModelo).filter(RutaModelo.id == ruta_id).first()
    if not db_ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada.")
    db.delete(db_ruta)
    db.commit()
    return {"detail": "Ruta eliminada exitosamente."}