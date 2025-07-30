from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class User(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID - Se genera automáticamente desde el _id de MongoDB, no es necesario enviarlo en POST"
    )

    name_profile: str = Field(
        description="Nombre visible del usuario en la plataforma",
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9' _-]+$",
        examples=["GamerMaster123", "Ana_López"]
    )

    email: str = Field(
        description="Correo electrónico del usuario",
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        examples=["usuario@example.com"]
    )

    password: str = Field(
        min_length=8,
        max_length=64,
        description="Contraseña segura. Mínimo 8 caracteres, incluyendo una mayúscula, un número y un carácter especial.",
        examples=["Password123!"]
    )

    date_birth: str = Field(
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Fecha de nacimiento en formato YYYY-MM-DD",
        examples=["2000-05-30"]
    )

    active: bool = Field(
        default=True,
        description="Estado activo del usuario"
    )

    admin: bool = Field(
        default=False,
        description="Rol administrador del sistema"
    )

    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, value: str):
        if not re.search(r"[A-Z]", value):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula.")
        if not re.search(r"\d", value):
            raise ValueError("La contraseña debe contener al menos un número.")
        if not re.search(r"[@$!%*?&]", value):
            raise ValueError("La contraseña debe contener al menos un carácter especial (@$!%*?&).")
        return value

__all__ = ["User"]
