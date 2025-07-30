from fastapi import APIRouter, Path, Body, status, Request
from typing import List
from models.developers import Developer, DeveloperPaginatedResponse


from controllers.developers import (
    create_developer, list_developers,
    get_developer_by_id, update_developer,
    disable_developer
)
from utils.security import validateadmin, validateuser

router = APIRouter(
    prefix="/developers",
    tags=["Developers"]
)

@router.post(
    "",
    summary="Crear nuevo desarrollador",
    response_model=Developer,
    status_code=status.HTTP_201_CREATED
)
@validateadmin
async def add_developer(request: Request, developer: Developer):
    return await create_developer(developer)

@router.get(
    "",
    summary="Listar desarrolladores activos",
    response_model=List[Developer]
)
@validateuser
async def get_developers(request: Request):
    return await list_developers()

@router.get(
    "/{dev_id}",
    summary="Obtener desarrollador por ID",
    response_model=Developer
)
@validateuser
async def get_developer(request: Request, dev_id: str = Path(..., description="ID del desarrollador")):
    return await get_developer_by_id(dev_id)

@router.put(
    "/{dev_id}",
    summary="Actualizar desarrollador existente"
)
@validateadmin
async def edit_developer(request: Request, dev_id: str, dev_data: dict = Body(...)):
    return await update_developer(dev_id, dev_data)

@router.delete(
    "/{dev_id}",
    summary="Desactivar desarrollador"
)
@validateadmin
async def remove_developer(request: Request, dev_id: str):
    return await disable_developer(dev_id)

@router.get("/", response_model=DeveloperPaginatedResponse)
async def list_all(skip: int = 0, limit: int = 10):
    return await list_developers(skip, limit)

