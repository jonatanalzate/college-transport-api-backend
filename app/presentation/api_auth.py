from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..domain.models.usuario import Usuario
from ..domain.models.empresa import Empresa
from ..domain.schemas.usuario_schemas import Usuario as UsuarioSchema
from ..domain.schemas.usuario_schemas import UsuarioCreate, UsuarioUpdate
from ..domain.schemas.empresa_schemas import Empresa as EmpresaSchema
from ..domain.schemas.empresa_schemas import EmpresaCreate, EmpresaUpdate
from ..data.database import get_db
from ..auth.security import (
    get_current_user, 
    get_password_hash, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    verify_password
)
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

# Crear dos routers separados
auth_router = APIRouter(tags=["auth"])  # Router para autenticación
usuarios_router = APIRouter(prefix="/usuarios", tags=["usuarios"])  # Router para gestión de usuarios

# Endpoint de autenticación en el router de auth
@auth_router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Primero intentar autenticar como usuario
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    if usuario and verify_password(form_data.password, usuario.hashed_password):
        if not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario inactivo"
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": usuario.email,
                "type": "usuario",
                "rol": usuario.rol,
                "empresa_id": usuario.empresa_id
            },
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_type": "usuario",
            "rol": usuario.rol
        }

    # Si no es usuario, intentar autenticar como empresa
    empresa = db.query(Empresa).filter(Empresa.email == form_data.username).first()
    if empresa and verify_password(form_data.password, empresa.hashed_password):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": empresa.email,
                "type": "empresa",
                "empresa_id": empresa.id
            },
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_type": "empresa"
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email o contraseña incorrectos",
        headers={"WWW-Authenticate": "Bearer"},
    )

@auth_router.post("/register/empresa", response_model=EmpresaSchema)
async def register_empresa(empresa: EmpresaCreate, db: Session = Depends(get_db)):
    db_empresa = db.query(Empresa).filter(Empresa.email == empresa.email).first()
    if db_empresa:
        raise HTTPException(
            status_code=400,
            detail="Email ya registrado"
        )
    hashed_password = get_password_hash(empresa.password)
    db_empresa = Empresa(
        email=empresa.email,
        nombre=empresa.nombre,
        hashed_password=hashed_password
    )
    db.add(db_empresa)
    db.commit()
    db.refresh(db_empresa)
    return db_empresa

@auth_router.post("/register/usuario", response_model=UsuarioSchema)
async def register_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # Verificar si el email ya existe
    db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(
            status_code=400,
            detail="Email ya registrado"
        )
    
    # Verificar si la empresa existe
    db_empresa = db.query(Empresa).filter(Empresa.id == usuario.empresa_id).first()
    if not db_empresa:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada"
        )
    
    hashed_password = get_password_hash(usuario.password)
    db_usuario = Usuario(
        email=usuario.email,
        nombre=usuario.nombre,
        hashed_password=hashed_password,
        rol=usuario.rol,
        empresa_id=usuario.empresa_id
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

# Los endpoints de usuarios en el router de usuarios
@usuarios_router.post("/", response_model=UsuarioSchema)
def create_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Verificar que el usuario actual es admin
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para crear usuarios"
        )

    # Verificar que el usuario pertenece a la misma empresa
    if usuario.empresa_id != current_user.empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puede crear usuarios para su propia empresa"
        )

    # Verificar si el email ya existe
    db_user = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    # Crear el usuario
    hashed_password = get_password_hash(usuario.password)
    db_usuario = Usuario(
        **usuario.dict(exclude={'password'}),
        hashed_password=hashed_password
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@usuarios_router.get("/", response_model=List[UsuarioSchema])
def get_usuarios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Solo mostrar usuarios de la misma empresa
    usuarios = db.query(Usuario).filter(
        Usuario.empresa_id == current_user.empresa_id
    ).all()
    return usuarios

@usuarios_router.get("/{usuario_id}", response_model=UsuarioSchema)
def get_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id,
        Usuario.empresa_id == current_user.empresa_id
    ).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return usuario

@usuarios_router.put("/{usuario_id}", response_model=UsuarioSchema)
def update_usuario(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para actualizar usuarios"
        )

    db_usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id,
        Usuario.empresa_id == current_user.empresa_id
    ).first()

    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    update_data = usuario_update.dict(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(db_usuario, field, value)

    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@usuarios_router.delete("/{usuario_id}")
def delete_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para eliminar usuarios"
        )

    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id,
        Usuario.empresa_id == current_user.empresa_id
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    db.delete(usuario)
    db.commit()
    return {"detail": "Usuario eliminado"}

# Exportar ambos routers
router = auth_router  # Para mantener compatibilidad con las importaciones existentes 