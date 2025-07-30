from fastapi import APIRouter, Path, Body, status, Request
from typing import List
from models.purchases import Purchase
from controllers.purchases import (
    create_purchase, list_purchases,
    get_purchase_by_id, update_purchase,
    disable_purchase
)
from utils.security import validateuser, validateadmin

router = APIRouter(prefix="/purchases", tags=["Purchases"])

@router.post(
    "",
    summary="Crear una nueva compra",
    response_model=Purchase,
    status_code=status.HTTP_201_CREATED
)
@validateuser
async def add_purchase(request: Request, purchase: Purchase):
    return await create_purchase(purchase)

@router.get(
    "",
    summary="Listar todas las compras activas",
    response_model=dict
)
@validateadmin
async def get_purchases(request: Request, skip: int = 0, limit: int = 10):
    return await list_purchases(skip, limit)

@router.get(
    "/{purchase_id}",
    summary="Obtener compra por ID",
    response_model=Purchase
)
@validateuser
async def get_purchase(request: Request, purchase_id: str = Path(..., description="ID de la compra")):
    return await get_purchase_by_id(purchase_id)

@router.put(
    "/{purchase_id}",
    summary="Actualizar compra existente"
)
@validateadmin
async def edit_purchase(request: Request, purchase_id: str, purchase_data: dict = Body(...)):
    return await update_purchase(purchase_id, purchase_data)

@router.delete(
    "/{purchase_id}",
    summary="Desactivar (no eliminar) una compra"
)
@validateadmin
async def remove_purchase(request: Request, purchase_id: str):
    return await disable_purchase(purchase_id)

@router.get("/")
@validateuser
async def get_purchases(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    user_id = None
    if not getattr(request.state, "admin", False):
        user_id = request.state.id
    return await list_purchases(skip=skip, limit=limit, user_id=user_id)