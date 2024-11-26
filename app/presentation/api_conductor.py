import csv
from io import StringIO
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.domain.models.conductor import Conductor as ConductorModelo
from app.domain.schemas.conductor_schemas import ConductorCrear, Conductor, ConductorActualizar
from app.data.database import get_db_for_empresa
from app.auth.security import get_current_empresa
from app.domain.models.empresa import Empresa
from typing import List

router = APIRouter()

@router.post("/conductores/", response_model=List[Conductor], tags=["Conductores"])
def crear_conductores(conductores: List[ConductorCrear],
                       empresa_actual: Empresa = Depends(get_current_empresa),
                       db: Session = Depends(get_db_for_empresa)):
    db = get_db_for_empresa(empresa_actual.email)
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

@router.post("/conductores/bulk", tags=["Conductores"])
async def crear_conductores_bulk(file: UploadFile = File(...),
                                   empresa_actual: Empresa = Depends(get_current_empresa),
                                   db: Session = Depends(get_db_for_empresa)):
    db = get_db_for_empresa(empresa_actual.email)
    contents = await file.read()
    decoded_contents = contents.decode('utf-8')
    csv_reader = csv.DictReader(StringIO(decoded_contents), delimiter=';')

    db_conductores = []
    errores = []

    for row in csv_reader:
        try:
            db_conductor = ConductorModelo(
                nombre=row['nombre'],
                cedula=row['cedula'],
                licencia=row['licencia'],
                telefono=row['telefono'],
                estado=row['estado'],
            )
            db.add(db_conductor)
            db_conductores.append(db_conductor)
        except Exception as e:
            errores.append(f"Error al procesar el conductor {row['cedula']}: {str(e)}")

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error: Conductor duplicado.")

    return {"conductores_insertados": len(db_conductores), "errores": errores}

@router.get("/conductores/", response_model=List[Conductor], tags=["Conductores"])
def leer_conductores(empresa_actual: Empresa = Depends(get_current_empresa),
                      db: Session = Depends(get_db_for_empresa)):
    db = get_db_for_empresa(empresa_actual.email)
    conductores = db.query(ConductorModelo).all()
    return [Conductor.model_validate(conductor.__dict__) for conductor in conductores]

@router.put("/conductor/{conductor_id}", response_model=Conductor, tags=["Conductores"])
async def modificar_conductor(conductor_id: str, conductor: Conductor,
                               empresa_actual: Empresa = Depends(get_current_empresa),
                               db: Session = Depends(get_db_for_empresa)):
    db = get_db_for_empresa(empresa_actual.email)
    db_conductor = db.query(ConductorModelo).filter(ConductorModelo.id == conductor_id).first()
    if not db_conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado.")
    for key, value in conductor.model_dump().items():
        setattr(db_conductor, key, value)
    db.commit()
    conductor_dict = {k: getattr(db_conductor, k) for k in Conductor.model_fields.keys()}
    return Conductor.model_validate(db_conductor.__dict__)

@router.patch("/conductor/{conductor_id}", response_model=Conductor, tags=["Conductores"])
async def modificar_conductor_parcial(conductor_id: str, conductor: ConductorActualizar,
                                       empresa_actual: Empresa = Depends(get_current_empresa),
                                       db: Session = Depends(get_db_for_empresa)):
    db = get_db_for_empresa(empresa_actual.email)
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

@router.get("/conductor/{conductor_id}", response_model=Conductor, tags=["Conductores"])
async def obtener_conductor(conductor_id: str,
                             empresa_actual: Empresa = Depends(get_current_empresa),
                             db: Session = Depends(get_db_for_empresa)):
    db = get_db_for_empresa(empresa_actual.email)
    db_conductor = db.query(ConductorModelo).filter(ConductorModelo.id == conductor_id).first()
    if not db_conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado.")
    return Conductor.model_validate(db_conductor.__dict__)

@router.delete("/conductor/{conductor_id}", response_model=dict, tags=["Conductores"])
async def eliminar_conductor(conductor_id: str,
                              empresa_actual: Empresa = Depends(get_current_empresa),
                              db: Session = Depends(get_db_for_empresa)):
    db = get_db_for_empresa(empresa_actual.email)
    db_conductor = db.query(ConductorModelo).filter(ConductorModelo.id == conductor_id).first()
    if not db_conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado.")
    db.delete(db_conductor)
    db.commit()
    return {"detail": "Conductor eliminado exitosamente."}