from pydantic import BaseModel, EmailStr
from typing import Optional

class EmpresaBase(BaseModel):
    nombre: str
    email: EmailStr

class EmpresaCreate(EmpresaBase):
    password: str

class EmpresaUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class Empresa(EmpresaBase):
    id: int

    class Config:
        from_attributes = True  # antes conocido como orm_mode