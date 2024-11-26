from pydantic import BaseModel, EmailStr

class EmpresaBase(BaseModel):
    nombre: str
    email: EmailStr
    nit: str

class EmpresaCreate(EmpresaBase):
    password: str

class Empresa(EmpresaBase):
    id: int
    
    class Config:
        from_attributes = True 