from fastapi import APIRouter, status, Path, Body
from models.contracts_types import ContractType
from controllers.contracts_types import (
    create_contract_type,
    list_contract_types,
    update_contract_type,
    disable_contract_type
)
from utils.security import validateadmin

router = APIRouter(prefix="/contract_types", tags=["Contract Types"])

@router.post(
    "",
    summary="Crear un nuevo tipo de contrato",
    response_model=ContractType,
    status_code=status.HTTP_201_CREATED
)
@validateadmin
async def add_contract_type(contract_type: ContractType):
    return await create_contract_type(contract_type)

@router.get(
    "",
    summary="Listar tipos de contrato activos",
    response_model=dict
)
@validateadmin
async def get_contract_types(skip: int = 0, limit: int = 10):
    return await list_contract_types(skip, limit)

@router.put(
    "/{contract_type_id}",
    summary="Actualizar tipo de contrato"
)
@validateadmin
async def edit_contract_type(
    contract_type_id: str = Path(..., description="ID del tipo de contrato"),
    contract_type_data: dict = Body(...)
):
    return await update_contract_type(contract_type_id, contract_type_data)

@router.delete(
    "/{contract_type_id}",
    summary="Desactivar (no eliminar) tipo de contrato"
)
@validateadmin
async def remove_contract_type(contract_type_id: str):
    return await disable_contract_type(contract_type_id)