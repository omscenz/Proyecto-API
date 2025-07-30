from fastapi import HTTPException
from bson import ObjectId
from models.games import Game
from utils.mongodb import get_collection

games_collection = get_collection("Games")

# Crear juego
async def create_game(game: Game):
    # Validar si ya existe un juego con el mismo título (ignorando mayúsculas/minúsculas)
    existing_game = games_collection.find_one({"title": {"$regex": f"^{game.title}$", "$options": "i"}})
    if existing_game:
        raise HTTPException(status_code=400, detail="Ya existe un juego con este título")

    game_dict = game.model_dump(exclude_unset=True)
    result = games_collection.insert_one(game_dict)
    game.id = str(result.inserted_id)
    return game

# Obtener todos los juegos activos con paginación
async def list_games(skip: int = 0, limit: int = 10):
    games_cursor = games_collection.find({"active": True}).skip(skip).limit(limit)
    games = [{**game, "id": str(game["_id"])} for game in games_cursor]
    total = games_collection.count_documents({"active": True})
    return {
        "games": games,
        "total": total,
        "skip": skip,
        "limit": limit
    }

# Obtener juego por ID con validación de ObjectId
async def get_game_by_id(game_id: str):
    if not ObjectId.is_valid(game_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    game = games_collection.find_one({"_id": ObjectId(game_id)})
    if not game:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    return {**game, "id": str(game["_id"])}

# Actualizar juego con validación de ObjectId
async def update_game(game_id: str, game_data: dict):
    if not ObjectId.is_valid(game_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    result = games_collection.update_one(
        {"_id": ObjectId(game_id)},
        {"$set": game_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    return {"message": "Juego actualizado correctamente"}

# Desactivar juego con validación de ObjectId
async def disable_game(game_id: str):
    if not ObjectId.is_valid(game_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    result = games_collection.update_one(
        {"_id": ObjectId(game_id)},
        {"$set": {"active": False}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    return {"message": "Juego desactivado"}
