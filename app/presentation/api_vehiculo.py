from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.domain.models.vehiculo import Vehiculo as VehiculoModelo
from app.domain.schemas.vehiculo_schemas import VehiculoCrear, Vehiculo, VehiculoActualizar
from app.data.database import get_db_for_empresa
from typing import List
import csv
from io import StringIO
from app.auth.security import get_current_empresa
from app.domain.models.empresa import Empresa
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/vehiculos/", response_model=List[Vehiculo], tags=["Vehiculos"])
def crear_vehiculos(vehiculos: List[VehiculoCrear], empresa_actual: Empresa = Depends(get_current_empresa)):
    db = empresa_actual.db
    db_vehiculos = []
    for vehiculo in vehiculos:
        db_vehiculo = VehiculoModelo(
            **vehiculo.model_dump(),
            empresa_id=empresa_actual.id
        )
        db.add(db_vehiculo)
        db_vehiculos.append(db_vehiculo)
    try:    
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error: Placa duplicada.")        
    return db_vehiculos

@router.post("/vehiculos/bulk", tags=["Vehiculos"])
async def crear_vehiculos_bulk(
    file: UploadFile = File(...),
    empresa_actual: Empresa = Depends(get_current_empresa)
):
    try:
        db = empresa_actual.db
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
                    estado_operativo=row['estado_operativo'],
                    empresa_id=empresa_actual.id
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
    except Exception as e:
        logger.error(f"Error al procesar archivo bulk: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar archivo: {str(e)}"
        )

@router.get("/vehiculos/", response_model=List[Vehiculo], tags=["Vehiculos"])
def leer_vehiculos(empresa_actual: Empresa = Depends(get_current_empresa)):
    logger.info(f"Obteniendo vehículos para empresa: {empresa_actual.email}")
    try:
        db = empresa_actual.db
        vehiculos = db.query(VehiculoModelo).filter(
            VehiculoModelo.empresa_id == empresa_actual.id
        ).all()
        logger.info(f"Encontrados {len(vehiculos)} vehículos")
        return vehiculos
    except Exception as e:
        logger.error(f"Error al obtener vehículos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener vehículos: {str(e)}"
        )

@router.put("/vehiculo/{vehiculo_id}", response_model=Vehiculo, tags=["Vehiculos"])
async def modificar_vehiculo(
    vehiculo_id: str, 
    vehiculo: Vehiculo, 
    empresa_actual: Empresa = Depends(get_current_empresa)
):
    try:
        db = empresa_actual.db
        db_vehiculo = db.query(VehiculoModelo).filter(
            VehiculoModelo.id == vehiculo_id,
            VehiculoModelo.empresa_id == empresa_actual.id
        ).first()
        
        if not db_vehiculo:
            raise HTTPException(status_code=404, detail="Vehículo no encontrado.")
            
        for key, value in vehiculo.model_dump().items():
            setattr(db_vehiculo, key, value)
            
        db.commit()
        return Vehiculo.model_validate(db_vehiculo.__dict__)
    except Exception as e:
        logger.error(f"Error al modificar vehículo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al modificar vehículo: {str(e)}"
        )

@router.patch("/vehiculo/{vehiculo_id}", response_model=Vehiculo, tags=["Vehiculos"])
async def actualizar_vehiculo_parcial(
    vehiculo_id: str, 
    vehiculo: VehiculoActualizar, 
    empresa_actual: Empresa = Depends(get_current_empresa)
):
    try:
        db = empresa_actual.db
        db_vehiculo = db.query(VehiculoModelo).filter(
            VehiculoModelo.id == vehiculo_id,
            VehiculoModelo.empresa_id == empresa_actual.id
        ).first()
        
        if not db_vehiculo:
            raise HTTPException(status_code=404, detail="Vehículo no encontrado.")
        
        for key, value in vehiculo.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(db_vehiculo, key, value)
        
        db.commit()
        return Vehiculo.model_validate(db_vehiculo.__dict__)
    except Exception as e:
        logger.error(f"Error al actualizar vehículo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar vehículo: {str(e)}"
        )

@router.get("/vehiculo/{vehiculo_placa}", response_model=Vehiculo, tags=["Vehiculos"])
async def leer_vehiculo(vehiculo_placa: str, empresa_actual: Empresa = Depends(get_current_empresa), db: Session = Depends(get_db_for_empresa)):
    db_vehiculo = db.query(VehiculoModelo).filter(VehiculoModelo.placa == vehiculo_placa).first()
    if not db_vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado.")
    return Vehiculo.model_validate(db_vehiculo.__dict__)

@router.delete("/vehiculo/{vehiculo_id}", response_model=dict, tags=["Vehiculos"])
async def eliminar_vehiculo(vehiculo_id: str, empresa_actual: Empresa = Depends(get_current_empresa), db: Session = Depends(get_db_for_empresa)):
    db_vehiculo = db.query(VehiculoModelo).filter(VehiculoModelo.id == vehiculo_id).first()
    if not db_vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado.")
    db.delete(db_vehiculo)
    db.commit()
    return {"detail": "Vehículo eliminado exitosamente."}