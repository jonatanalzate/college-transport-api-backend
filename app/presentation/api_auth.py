from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.auth.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_empresa
from app.data.database import get_db, init_empresa_db
from app.domain.models.empresa import Empresa
from app.domain.schemas.empresa_schemas import EmpresaCreate, Empresa as EmpresaSchema

router = APIRouter(tags=["Autenticación"])

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.email == form_data.username).first()
    if not empresa or not verify_password(form_data.password, empresa.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": empresa.email, "empresa_id": empresa.id},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/empresas/", response_model=EmpresaSchema)
def crear_empresa(empresa: EmpresaCreate, db: Session = Depends(get_db)):
    db_empresa = db.query(Empresa).filter(Empresa.email == empresa.email).first()
    if db_empresa:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    from app.auth.security import get_password_hash
    hashed_password = get_password_hash(empresa.password)
    db_empresa = Empresa(
        nombre=empresa.nombre,
        email=empresa.email,
        nit=empresa.nit,
        hashed_password=hashed_password
    )
    db.add(db_empresa)
    db.commit()
    db.refresh(db_empresa)
    
    init_empresa_db(db_empresa.email)
    
    return db_empresa 