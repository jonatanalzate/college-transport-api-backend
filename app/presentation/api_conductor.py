import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.domain.models.conductor import Conductor as ConductorModelo
from app.domain.schemas.conductor_schemas import ConductorCrear, Conductor, ConductorActualizar
from app.auth.security import get_current_empresa
from app.domain.models.empresa import Empresa
from typing import List
from pydantic import ValidationError

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/conductores/", response_model=List[Conductor], tags=["Conductores"])
def crear_conductores(conductores: List[ConductorCrear], 
                     empresa_actual: Empresa = Depends(get_current_empresa)):
    try:
        # Log del payload recibido
        logger.info(f"Payload recibido: {conductores}")
        logger.info(f"Tipo de payload: {type(conductores)}")
        
        if not isinstance(conductores, list):
            raise HTTPException(
                status_code=422,
                detail="Se espera un array de conductores"
            )
            
        db = empresa_actual.db
        db_conductores = []
        
        for conductor in conductores:
            logger.info(f"Procesando conductor: {conductor.model_dump()}")
            db_conductor = ConductorModelo(
                **conductor.model_dump(),
                empresa_id=empresa_actual.id
            )
            db.add(db_conductor)
            db_conductores.append(db_conductor)
        
        db.commit()
        
        for conductor in db_conductores:
            db.refresh(conductor)
        
        conductores_dict = []
        for conductor in db_conductores:
            conductor_dict = {
                "id": conductor.id,
                "nombre": conductor.nombre,
                "cedula": conductor.cedula,
                "licencia": conductor.licencia,
                "telefono": conductor.telefono,
                "estado": conductor.estado,
                "empresa_id": conductor.empresa_id
            }
            conductores_dict.append(conductor_dict)
        
        result = [Conductor.model_validate(c) for c in conductores_dict]
        logger.info(f"Conductores creados exitosamente: {len(result)}")
        return result
        
    except ValidationError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error al crear conductores: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear conductores: {str(e)}"
        )

@router.get("/conductores/", response_model=List[Conductor], tags=["Conductores"])
def leer_conductores(empresa_actual: Empresa = Depends(get_current_empresa)):
    try:
        db = empresa_actual.db
        conductores = db.query(ConductorModelo).filter(
            ConductorModelo.empresa_id == empresa_actual.id
        ).all()
        return conductores
    except Exception as e:
        logger.error(f"Error al obtener conductores: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener conductores: {str(e)}"
        )

# ... resto de los endpoints con cambios similares