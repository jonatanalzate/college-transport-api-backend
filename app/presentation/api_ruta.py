import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.domain.models.ruta import Ruta as RutaModelo
from app.domain.schemas.ruta_schemas import RutaCrear, Ruta, RutaActualizar
from app.auth.security import get_current_empresa
from app.domain.models.empresa import Empresa
from typing import List

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/rutas/", response_model=Ruta, tags=["Rutas"])
def crear_ruta(ruta: RutaCrear, empresa_actual: Empresa = Depends(get_current_empresa)):
    try:
        db = empresa_actual.db
        db_ruta = RutaModelo(**ruta.model_dump(), empresa_id=empresa_actual.id)
        db.add(db_ruta)
        db.commit()
        db.refresh(db_ruta)
        return db_ruta
    except Exception as e:
        logger.error(f"Error al crear ruta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear ruta: {str(e)}"
        )

@router.get("/rutas/", response_model=List[Ruta], tags=["Rutas"])
def leer_rutas(empresa_actual: Empresa = Depends(get_current_empresa)):
    try:
        db = empresa_actual.db
        rutas = db.query(RutaModelo).filter(
            RutaModelo.empresa_id == empresa_actual.id
        ).all()
        return rutas
    except Exception as e:
        logger.error(f"Error al obtener rutas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener rutas: {str(e)}"
        )

@router.post("/rutas/bulk", tags=["Rutas"])
async def crear_rutas_bulk(file: UploadFile = File(...), 
                            empresa_actual: Empresa = Depends(get_current_empresa)):
    contents = await file.read()
    decoded_contents = contents.decode('utf-8')
    csv_reader = csv.DictReader(StringIO(decoded_contents), delimiter=';')

    db = empresa_actual.db
    db_rutas = []
    errores = []

    for row in csv_reader:
        try:
            db_ruta = RutaModelo(
                nombre=row['nombre'],
                codigo=row['codigo'],
                origen=row['origen'],
                destino=row['destino'],
                duracion_estimada=int(row['duracion_estimada']),
            )
            db.add(db_ruta)
            db_rutas.append(db_ruta)
        except Exception as e:
            errores.append(f"Error al procesar la ruta {row['codigo']}: {str(e)}")

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error: Ruta duplicada.")

    return {"rutas_insertadas": len(db_rutas), "errores": errores}

@router.put("/ruta/{ruta_id}", response_model=Ruta, tags=["Rutas"])
async def modificar_ruta(ruta_id: str, ruta: Ruta, 
                          empresa_actual: Empresa = Depends(get_current_empresa)):
    db = empresa_actual.db
    db_ruta = db.query(RutaModelo).filter(RutaModelo.id == ruta_id).first()
    if not db_ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada.")
    for key, value in ruta.model_dump().items():
        setattr(db_ruta, key, value)
    db.commit()
    ruta_dict = {k: getattr(db_ruta, k) for k in Ruta.model_fields.keys()}
    return Ruta.model_validate(db_ruta.__dict__)

@router.patch("/ruta/{ruta_id}", response_model=Ruta, tags=["Rutas"])
async def modificar_ruta_parcial(ruta_id: str, ruta: RutaActualizar, 
                                  empresa_actual: Empresa = Depends(get_current_empresa)):
    db = empresa_actual.db
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
async def leer_ruta(ruta_id: str,
                   empresa_actual: Empresa = Depends(get_current_empresa)):
    db = empresa_actual.db
    db_ruta = db.query(RutaModelo).filter(RutaModelo.id == ruta_id).first()
    if not db_ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrado.")
    return Ruta.model_validate(db_ruta.__dict__)

@router.delete("/ruta/{ruta_id}", response_model=dict, tags=["Rutas"])
async def eliminar_ruta(ruta_id: str, 
                          empresa_actual: Empresa = Depends(get_current_empresa)):
    db = empresa_actual.db
    db_ruta = db.query(RutaModelo).filter(RutaModelo.id == ruta_id).first()
    if not db_ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada.")
    db.delete(db_ruta)
    db.commit()
    return {"detail": "Ruta eliminada exitosamente."}