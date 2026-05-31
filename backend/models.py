from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class ClienteCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=80)
    email: EmailStr
    telefone: str

    @field_validator('telefone')
    @classmethod
    def validar_telefone(cls, v):
    # Remove tudo que não for dígito
        digits = re.sub(r'\D', '', v)
        if len(digits) not in (10, 11):
           raise ValueError('Telefone deve ter 10 ou 11 dígitos')
    # Formata automaticamente (opcional)
        return v  # ou retorna o valor original

class PedidoCreate(BaseModel):
    id_cliente: int = Field(..., gt=0)
    produto: str = Field(..., min_length=1, max_length=100)
    valor: float = Field(..., gt=0)