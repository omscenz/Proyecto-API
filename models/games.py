from ast import List
from pydantic import BaseModel, Field
from typing import Optional
from typing import List
from datetime import date

class Game(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID (se genera automáticamente)"
    )

    title: str = Field(
        description="Título del videojuego",
        min_length=1,
        max_length=100,
        examples=["Elden Ring"]
    )

    description: str = Field(
        description="Descripción del videojuego",
        min_length=10,
        max_length=500
    )

    release_date: date = Field(
        description="Fecha de salida del videojuego",
        examples=["2024-10-01"]
    )

    price: float = Field(
        ge=0,
        description="Precio del videojuego"
    )

    developer_id: str = Field(
        description="ID del desarrollador (referencia a Developers)"
    )

    status: str = Field(
        description="Estado del juego: demo, oferta, gratis, completo, etc.",
        examples=["demo", "oferta", "gratis", "completo"]
    )

    active: bool = Field(
        default=True,
        description="Estado activo/inactivo del juego"
    )

class GamePaginatedResponse(BaseModel):
    games: List[Game]
    total: int
    skip: int
    limit: int

    __all__ = ["Game"]