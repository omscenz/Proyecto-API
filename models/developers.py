from pydantic import BaseModel, Field
from typing import List, Optional

class Developer(BaseModel):
    id: Optional[str] = Field(default=None, description="MongoDB ID generado automáticamente")
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del desarrollador")
    country: Optional[str] = Field(None, description="País de origen del desarrollador")
    founded_year: Optional[int] = Field(None, ge=1900, le=2100, description="Año de fundación")
    active: bool = Field(default=True, description="Estado activo/inactivo del desarrollador")

class DeveloperPaginatedResponse(BaseModel):
    developers: List[Developer]
    total: int
    skip: int
    limit: int

    __all__ = ["Developer"]