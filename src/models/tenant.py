from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
from src.models.pyobjectid import PyObjectId
from validate_docbr import CPF, CNPJ

class TenantCreate(BaseModel):
    establishment_name: str = Field(..., json_schema_extra={"example": "Tutto Barbershop"})
    phone: str = Field(..., json_schema_extra={"example": "5511999999999"})
    cpf_cnpj: str = Field(..., json_schema_extra={"example": "12.345.678/0001-90"})
    business_address: str = Field(..., json_schema_extra={"example": "Rua das Flores, 123"})
    responsible_name: Optional[str] = Field(None, json_schema_extra={"example": "João Silva"})
    responsible_email: Optional[str] = Field(None, json_schema_extra={"example": "joao@email.com"})
    business_name: Optional[str] = Field(None, json_schema_extra={"example": "Silva & Silva LTDA"})
    domain: Optional[str] = Field(None, json_schema_extra={"example": "tutto.barbershop.com"})
    token: Optional[str] = Field(None, json_schema_extra={"example": "random-auth-token"})

    @field_validator("cpf_cnpj")
    @classmethod
    def validate_document(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        
        # Remove formatting
        clean_doc = "".join(filter(str.isdigit, v))
        
        if len(clean_doc) == 11:
            if not CPF().validate(clean_doc):
                raise ValueError("Invalid CPF")
        elif len(clean_doc) == 14:
            if not CNPJ().validate(clean_doc):
                raise ValueError("Invalid CNPJ")
        else:
            raise ValueError("Document must be a valid CPF (11 digits) or CNPJ (14 digits)")
        
        return v

class TenantOut(BaseModel):
    id: PyObjectId = Field(..., alias="id")
    establishment_name: str
    phone: str
    cpf_cnpj: str
    business_address: str
    responsible_name: Optional[str] = None
    responsible_email: Optional[str] = None
    business_name: Optional[str] = None
    domain: Optional[str]
    token: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
