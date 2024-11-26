import csv
from io import StringIO
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.domain.models.trayecto import Trayecto as TrayectoModelo
from app.domain.schemas.trayecto_schemas import TrayectoCrear, Trayecto, TrayectoActualizar
from app.data.database import get_db_for_empresa
from app.auth.security import get_current_empresa
from app.domain.models.empresa import Empresa
from typing import List
from sqlalchemy.orm import joinedload
from sqlalchemy import and_, or_

router = APIRouter()

def verificar_disponibilidad(db: Session, fecha, hora_salida, hora_llegada, conductor_id=None, vehiculo_id=None, trayecto_id=None):
    """
    Verifica si un conductor o vehículo está disponible en el horario especificado
    """
    query = db.query(TrayectoModelo).filter(
        TrayectoModelo.fecha == fecha,
        or_(
            and_(
                TrayectoModelo.hora_salida <= hora_llegada,
                TrayectoModelo.hora_llegada >= hora_salida
            )
        )
    )
    
    if conductor_id:
        query = query.filter(TrayectoModelo.conductor_id == conductor_id)
    
    if vehiculo_id:
        query = query.filter(TrayectoModelo.vehiculo_id == vehiculo_id)
    
    if trayecto_id:
        query = query.filter(TrayectoModelo.id != trayecto_id)
    
    conflicto = query.first()
    
    if conflicto:
        if conductor_id and conflicto.conductor_id == conductor_id:
            raise HTTPException(
                status_code=400,
                detail=f"El conductor ya está asignado a otro trayecto en ese horario (ID: {conflicto.id})"
            )
        if vehiculo_id and conflicto.vehiculo_id == vehiculo_id:
            raise HTTPException(
                status_code=400,
                detail=f"El vehículo ya está asignado a otro trayecto en ese horario (ID: {conflicto.id})"
            )

@router.post("/trayectos/", response_model=Trayecto, tags=["Trayectos"])
def crear_trayecto(trayecto: TrayectoCrear,
                   empresa_actual: Empresa = Depends(get_current_empresa),
                   db: Session = Depends(get_db_for_empresa)):
    db = get_db_for_empresa(empresa_actual.email)
    db_trayecto = TrayectoModelo(**trayecto.model_dump())
    db.add(db_trayecto)
    db.commit()
    db.refresh(db_trayecto)
    return db_trayecto

@router.get("/trayectos/", response_model=List[Trayecto], tags=["Trayectos"])
def leer_trayectos(empresa_actual: Empresa = Depends(get_current_empresa),
                   db: Session = Depends(get_db_for_empresa)):
    db = get_db_for_empresa(empresa_actual.email)
    return db.query(TrayectoModelo).all()

@router.post("/trayectos/bulk", tags=["Trayectos"])
async def crear_trayectos_bulk(file: UploadFile = File(...), db: Session = Depends(get_db_for_empresa)):
    contents = await file.read()
    decoded_contents = contents.decode('utf-8')
    csv_reader = csv.DictReader(StringIO(decoded_contents), delimiter=';')

    db_trayectos = []
    errores = []

    for row in csv_reader:
        try:
            # Verificar disponibilidad antes de crear
            verificar_disponibilidad(
                db,
                row['fecha'],
                row['hora_salida'],
                row['hora_llegada'],
                row.get('conductor_id'),
                row.get('vehiculo_id')
            )
            db_trayecto = TrayectoModelo(
                # Asigna los campos necesarios
                fecha=row['fecha'],
                hora_salida=row['hora_salida'],
                hora_llegada=row['hora_llegada'],
                conductor_id=row.get('conductor_id'),
                vehiculo_id=row.get('vehiculo_id'),
                ruta_id=row['ruta_id'],
            )
            db.add(db_trayecto)
            db_trayectos.append(db_trayecto)
        except Exception as e:
            errores.append(f"Error al procesar el trayecto: {str(e)}")

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error: Trayecto duplicado.")

    return {"trayectos_insertados": len(db_trayectos), "errores": errores}

@router.get("/trayecto/{trayecto_id}", response_model=Trayecto, tags=["Trayectos"])
async def leer_trayecto(trayecto_id: str,
                       empresa_actual: Empresa = Depends(get_current_empresa),
                       db: Session = Depends(get_db_for_empresa)):
    db_trayecto = db.query(TrayectoModelo).options(
        joinedload(TrayectoModelo.ruta),
        joinedload(TrayectoModelo.conductor),
        joinedload(TrayectoModelo.vehiculo)
    ).filter(TrayectoModelo.id == trayecto_id).first()
    if not db_trayecto:
        raise HTTPException(status_code=404, detail="Trayecto no encontrado.")
    return db_trayecto

@router.delete("/trayecto/{trayecto_id}", response_model=dict, tags=["Trayectos"])
async def eliminar_trayecto(trayecto_id: str, db: Session = Depends(get_db_for_empresa)):
    db_trayecto = db.query(TrayectoModelo).filter(TrayectoModelo.id == trayecto_id).first()
    if not db_trayecto:
        raise HTTPException(status_code=404, detail="Trayecto no encontrado.")
    db.delete(db_trayecto)
    db.commit()
    return {"detail": "Trayecto eliminado exitosamente."}