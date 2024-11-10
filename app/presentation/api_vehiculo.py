from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.domain.models.vehiculo import Vehiculo as VehiculoModelo
from app.domain.schemas.vehiculo_schemas import VehiculoCrear, Vehiculo, VehiculoActualizar
from app.data.database import get_db
from typing import List

router = APIRouter()

@router.post("/vehiculos/", response_model=List[Vehiculo], tags=["Vehiculo"])
def crear_vehiculos(vehiculos: List[VehiculoCrear], db: Session = Depends(get_db)): 
    db_vehiculos = []
    for vehiculo in vehiculos:
        db_vehiculo = VehiculoModelo(**vehiculo.model_dump())
        db.add(db_vehiculo)
        db_vehiculos.append(db_vehiculo)
    try:    
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error: Placa duplicada.")        
    return db_vehiculos

@router.get("/vehiculos/", response_model=List[Vehiculo], tags=["Vehiculo"])
def leer_vehiculos(db: Session = Depends(get_db)):
    vehicles = db.query(VehiculoModelo).all()
    return [Vehiculo.model_validate(vehiculo.__dict__) for vehiculo in vehicles]

@router.put("/vehiculo/{vehiculo_id}", response_model=Vehiculo, tags=["Vehiculo"])
async def modificar_vehiculo(vehiculo_id: str, vehiculo: Vehiculo, db: Session = Depends(get_db)):
    db_vehiculo = db.query(VehiculoModelo).filter(VehiculoModelo.id == vehiculo_id).first()
    if not db_vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado.")
    for key, value in vehiculo.model_dump().items():
        setattr(db_vehiculo, key, value)
    db.commit()
    vehiculo_dict = {k: getattr(db_vehiculo, k) for k in Vehiculo.model_fields.keys()}
    return Vehiculo.model_validate(db_vehiculo.__dict__)

@router.patch("/vehiculo/{vehiculo_id}", response_model=Vehiculo, tags=["Vehiculo"])
async def modificar_vehiculo_parcial(vehiculo_id: str, vehiculo: VehiculoActualizar, db: Session = Depends(get_db)):
    db_vehiculo = db.query(VehiculoModelo).filter(VehiculoModelo.id == vehiculo_id).first()
    if not db_vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado.")
    
    # Solo actualizar los campos que se envían en la solicitud
    for key, value in vehiculo.model_dump(exclude_unset=True).items():
        if value is not None:  # Asegúrate de que el valor no sea None
            setattr(db_vehiculo, key, value)
    
    db.commit()
    
    # Crear un diccionario con los valores actualizados
    vehiculo_dict = {
        "id": db_vehiculo.id,
        "marca": db_vehiculo.marca,
        "placa": db_vehiculo.placa,
        "modelo": db_vehiculo.modelo,
        "lateral": db_vehiculo.lateral,
        "año_de_fabricación": db_vehiculo.año_de_fabricación,
        "capacidad_pasajeros": db_vehiculo.capacidad_pasajeros,
        "estado_operativo": db_vehiculo.estado_operativo,
    }
    
    return Vehiculo.model_validate(vehiculo_dict)

@router.get("/vehiculo/{vehiculo_placa}", response_model=Vehiculo, tags=["Vehiculo"])
async def obtener_vehiculo(vehiculo_placa: str, db: Session = Depends(get_db)):
    db_vehiculo = db.query(VehiculoModelo).filter(VehiculoModelo.placa == vehiculo_placa).first()
    if not db_vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado.")
    return Vehiculo.model_validate(db_vehiculo.__dict__)

@router.delete("/vehiculo/{vehiculo_id}", response_model=dict, tags=["Vehiculo"])
async def eliminar_vehiculo(vehiculo_id: str, db: Session = Depends(get_db)):
    db_vehiculo = db.query(VehiculoModelo).filter(VehiculoModelo.placa == vehiculo_id).first()
    if not db_vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado.")
    db.delete(db_vehiculo)
    db.commit()
    return {"detail": "Vehículo eliminado exitosamente."}