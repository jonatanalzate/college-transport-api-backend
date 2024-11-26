import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from app.domain.models.trayecto import Trayecto as TrayectoModelo
from app.domain.schemas.trayecto_schemas import TrayectoCrear, Trayecto, TrayectoActualizar
from app.auth.security import get_current_empresa
from app.domain.models.empresa import Empresa
from typing import List
import csv
from io import StringIO
from datetime import date

logger = logging.getLogger(__name__)
router = APIRouter()

def verificar_disponibilidad(db: Session, fecha, hora_salida, hora_llegada, 
                           conductor_id=None, vehiculo_id=None, trayecto_id=None,
                           empresa_id=None):
    """Verifica disponibilidad incluyendo filtro por empresa"""
    query = db.query(TrayectoModelo).filter(
        TrayectoModelo.fecha == fecha,
        TrayectoModelo.empresa_id == empresa_id
    )
    # ... resto de la lógica de verificación

@router.post("/trayectos/", response_model=Trayecto, tags=["Trayectos"])
def crear_trayecto(trayecto: TrayectoCrear, 
                   empresa_actual: Empresa = Depends(get_current_empresa)):
    try:
        db = empresa_actual.db
        verificar_disponibilidad(
            db, 
            trayecto.fecha, 
            trayecto.hora_salida, 
            trayecto.hora_llegada,
            trayecto.conductor_id,
            trayecto.vehiculo_id,
            empresa_id=empresa_actual.id
        )
        
        db_trayecto = TrayectoModelo(
            **trayecto.model_dump(),
            empresa_id=empresa_actual.id
        )
        db.add(db_trayecto)
        db.commit()
        db.refresh(db_trayecto)
        return db_trayecto
    except Exception as e:
        logger.error(f"Error al crear trayecto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear trayecto: {str(e)}"
        )

@router.get("/trayectos/", response_model=List[Trayecto], tags=["Trayectos"])
def leer_trayectos(empresa_actual: Empresa = Depends(get_current_empresa)):
    try:
        db = empresa_actual.db
        trayectos = db.query(TrayectoModelo).filter(
            TrayectoModelo.empresa_id == empresa_actual.id
        ).all()
        return trayectos
    except Exception as e:
        logger.error(f"Error al obtener trayectos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener trayectos: {str(e)}"
        )

@router.post("/trayectos/bulk", tags=["Trayectos"])
async def crear_trayectos_bulk(
    file: UploadFile = File(...),
    empresa_actual: Empresa = Depends(get_current_empresa)
):
    try:
        db = empresa_actual.db
        contents = await file.read()
        decoded_contents = contents.decode('utf-8')
        csv_reader = csv.DictReader(StringIO(decoded_contents), delimiter=';')

        db_trayectos = []
        errores = []

        for row in csv_reader:
            try:
                verificar_disponibilidad(
                    db,
                    row['fecha'],
                    row['hora_salida'],
                    row['hora_llegada'],
                    row.get('conductor_id'),
                    row.get('vehiculo_id'),
                    empresa_id=empresa_actual.id
                )
                
                db_trayecto = TrayectoModelo(
                    fecha=row['fecha'],
                    hora_salida=row['hora_salida'],
                    hora_llegada=row['hora_llegada'],
                    conductor_id=row.get('conductor_id'),
                    vehiculo_id=row.get('vehiculo_id'),
                    ruta_id=row['ruta_id'],
                    empresa_id=empresa_actual.id
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
    except Exception as e:
        logger.error(f"Error al procesar archivo bulk: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar archivo: {str(e)}"
        )

@router.get("/trayecto/{trayecto_id}", response_model=Trayecto, tags=["Trayectos"])
async def leer_trayecto(
    trayecto_id: str,
    empresa_actual: Empresa = Depends(get_current_empresa)
):
    try:
        db = empresa_actual.db
        db_trayecto = db.query(TrayectoModelo).options(
            joinedload(TrayectoModelo.ruta),
            joinedload(TrayectoModelo.conductor),
            joinedload(TrayectoModelo.vehiculo)
        ).filter(
            TrayectoModelo.id == trayecto_id,
            TrayectoModelo.empresa_id == empresa_actual.id
        ).first()
        
        if not db_trayecto:
            raise HTTPException(status_code=404, detail="Trayecto no encontrado.")
        return db_trayecto
    except Exception as e:
        logger.error(f"Error al obtener trayecto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener trayecto: {str(e)}"
        )

@router.delete("/trayecto/{trayecto_id}", response_model=dict, tags=["Trayectos"])
async def eliminar_trayecto(
    trayecto_id: str,
    empresa_actual: Empresa = Depends(get_current_empresa)
):
    try:
        db = empresa_actual.db
        db_trayecto = db.query(TrayectoModelo).filter(
            TrayectoModelo.id == trayecto_id,
            TrayectoModelo.empresa_id == empresa_actual.id
        ).first()
        
        if not db_trayecto:
            raise HTTPException(status_code=404, detail="Trayecto no encontrado.")
            
        db.delete(db_trayecto)
        db.commit()
        return {"detail": "Trayecto eliminado exitosamente."}
    except Exception as e:
        logger.error(f"Error al eliminar trayecto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar trayecto: {str(e)}"
        )

@router.get("/trayectos/activos/", response_model=List[Trayecto], tags=["Trayectos"])
def leer_trayectos_activos(empresa_actual: Empresa = Depends(get_current_empresa)):
    try:
        db = empresa_actual.db
        trayectos = db.query(TrayectoModelo).filter(
            TrayectoModelo.empresa_id == empresa_actual.id,
            TrayectoModelo.fecha >= date.today()  # Solo trayectos desde hoy
        ).order_by(TrayectoModelo.fecha, TrayectoModelo.hora_salida).all()
        return trayectos
    except Exception as e:
        logger.error(f"Error al obtener trayectos activos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener trayectos activos: {str(e)}"
        )