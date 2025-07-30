from fastapi import APIRouter
from controllers.games import (
    create_game, list_games, get_game_by_id,
    update_game, disable_game
)
from models.games import Game, GamePaginatedResponse
from typing import List

router = APIRouter(prefix="/games", tags=["Games"])

@router.post("/", response_model=Game)
async def create(game: Game):
    return await create_game(game)

@router.get("/", response_model=GamePaginatedResponse)
async def list_all(skip: int = 0, limit: int = 10):
    return await list_games(skip, limit)


@router.get("/{game_id}", response_model=Game)
async def get_by_id(game_id: str):
    return await get_game_by_id(game_id)

@router.put("/{game_id}")
async def update(game_id: str, game_data: dict):
    return await update_game(game_id, game_data)

@router.delete("/{game_id}")
async def disable(game_id: str):
    return await disable_game(game_id)

print("Se cargó routes.games")