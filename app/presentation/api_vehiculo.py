from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.domain.models.vehiculo import Vehiculo as VehiculoModelo
from app.domain.schemas.vehiculo_schemas import VehiculoCrear, Vehiculo, VehiculoActualizar
from app.data.database import get_db
from typing import List
import csv
from io import StringIO

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

@router.post("/vehiculos/bulk", tags=["Vehiculo"])
async def crear_vehiculos_bulk(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    decoded_contents = contents.decode('utf-8')
    csv_reader = csv.DictReader(StringIO(decoded_contents), delimiter=';')

    db_vehiculos = []
    errores = []

    for row in csv_reader:
        try:
            db_vehiculo = VehiculoModelo(
                marca=row['marca'],
                placa=row['placa'],
                modelo=row['modelo'],
                lateral=row['lateral'],
                año_de_fabricacion=int(row['año_de_fabricacion']),
                capacidad_pasajeros=int(row['capacidad_pasajeros']),
                estado_operativo=row['estado_operativo']
            )
            db.add(db_vehiculo)
            db_vehiculos.append(db_vehiculo)
        except Exception as e:
            errores.append(f"Error al procesar el vehículo {row['placa']}: {str(e)}")

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error: Placa duplicada.")

    return {"vehiculos_insertados": len(db_vehiculos), "errores": errores}

@router.get("/vehiculos/", response_model=List[Vehiculo], tags=["Vehiculo"])
def leer_vehiculos(db: Session = Depends(get_db)):
    vehiculos = db.query(VehiculoModelo).all()
    return [Vehiculo.model_validate(vehiculo.__dict__) for vehiculo in vehiculos]

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
        "año_de_fabricacion": db_vehiculo.año_de_fabricacion,
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
    db_vehiculo = db.query(VehiculoModelo).filter(VehiculoModelo.id == vehiculo_id).first()
    if not db_vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado.")
    db.delete(db_vehiculo)
    db.commit()
    return {"detail": "Vehículo eliminado exitosamente."}