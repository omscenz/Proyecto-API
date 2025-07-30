from pydantic import BaseModel, Field
from typing import Optional

class ContractType(BaseModel):
    id: Optional[str] = Field(default=None, description="MongoDB ID generado automáticamente")
    description: str = Field(..., min_length=3, max_length=50, description="Descripción del tipo de contrato")
    active: bool = Field(default=True, description="Estado activo/inactivo del tipo de contrato")

__all__ = ["ContractType"]
