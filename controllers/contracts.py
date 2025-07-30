from fastapi import HTTPException
from bson import ObjectId
from models.contracts import Contract
from utils.mongodb import get_collection
from pipelines.contracts_pipelines import check_existing_active_contract_pipeline  

contracts_collection = get_collection("contracts")
developers_collection = get_collection("developers")
games_collection = get_collection("games")
contract_types_collection = get_collection("contract_types")

async def create_contract(contract: Contract):
    # Validar IDs válidos
    for id_field in [contract.developer_id, contract.game_id, contract.type_contract_id]:
        if not ObjectId.is_valid(id_field):
            raise HTTPException(status_code=400, detail=f"ID inválido: {id_field}")

    # Validar developer activo
    developer = developers_collection.find_one({"_id": ObjectId(contract.developer_id), "active": True})
    if not developer:
        raise HTTPException(status_code=400, detail="Desarrollador no válido o inactivo")

    # Validar juego activo y pertenece al developer
    game = games_collection.find_one({
        "_id": ObjectId(contract.game_id),
        "active": True,
        "developer_id": contract.developer_id
    })
    if not game:
        raise HTTPException(status_code=400, detail="Juego no válido, inactivo o no pertenece al desarrollador")

    # Validar tipo de contrato activo
    contract_type = contract_types_collection.find_one({"_id": ObjectId(contract.type_contract_id), "active": True})
    if not contract_type:
        raise HTTPException(status_code=400, detail="Tipo de contrato inválido o inactivo")

    # Validar fechas
    if contract.end_date and contract.end_date < contract.start_date:
        raise HTTPException(status_code=400, detail="La fecha final no puede ser anterior a la fecha de inicio")

    # === Validación compleja con pipeline: No permitir contratos activos duplicados ===
    pipeline = check_existing_active_contract_pipeline(contract.developer_id, contract.game_id)
    existing_contracts = list(contracts_collection.aggregate(pipeline))
    if existing_contracts and existing_contracts[0].get("existing_contracts", 0) > 0:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un contrato activo para este desarrollador y juego."
        )
    # === Fin validación pipeline ===

    # Insertar contrato
    contract_dict = contract.model_dump(exclude_unset=True)
    result = contracts_collection.insert_one(contract_dict)
    contract.id = str(result.inserted_id)
    return contract


async def list_contracts(skip: int = 0, limit: int = 10):
    cursor = contracts_collection.find({"active": True}).skip(skip).limit(limit)
    contracts = []
    for doc in cursor:
        doc['id'] = str(doc['_id'])
        del doc['_id']
        contracts.append(Contract(**doc))
    total = contracts_collection.count_documents({"active": True})
    return {
        "contracts": contracts,
        "total": total,
        "skip": skip,
        "limit": limit
    }

async def get_contract_by_id(contract_id: str):
    if not ObjectId.is_valid(contract_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    doc = contracts_collection.find_one({"_id": ObjectId(contract_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    doc['id'] = str(doc['_id'])
    del doc['_id']
    return Contract(**doc)

async def update_contract(contract_id: str, contract_data: dict):
    if not ObjectId.is_valid(contract_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    if "developer_id" in contract_data:
        if not ObjectId.is_valid(contract_data["developer_id"]) or not developers_collection.find_one({"_id": ObjectId(contract_data["developer_id"]), "active": True}):
            raise HTTPException(status_code=400, detail="Desarrollador inválido o inactivo")

    if "game_id" in contract_data:
        if not ObjectId.is_valid(contract_data["game_id"]) or not games_collection.find_one({"_id": ObjectId(contract_data["game_id"]), "active": True, "developer_id": contract_data.get("developer_id", None)}):
            raise HTTPException(status_code=400, detail="Juego inválido, inactivo o no pertenece al desarrollador")

    if "type_contract_id" in contract_data:
        if not ObjectId.is_valid(contract_data["type_contract_id"]) or not contract_types_collection.find_one({"_id": ObjectId(contract_data["type_contract_id"]), "active": True}):
            raise HTTPException(status_code=400, detail="Tipo de contrato inválido o inactivo")

    if "start_date" in contract_data and "end_date" in contract_data:
        if contract_data["end_date"] and contract_data["end_date"] < contract_data["start_date"]:
            raise HTTPException(status_code=400, detail="La fecha final no puede ser anterior a la fecha de inicio")

    result = contracts_collection.update_one({"_id": ObjectId(contract_id)}, {"$set": contract_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")

    return {"message": "Contrato actualizado correctamente"}

async def disable_contract(contract_id: str):
    if not ObjectId.is_valid(contract_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    result = contracts_collection.update_one({"_id": ObjectId(contract_id)}, {"$set": {"active": False}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    return {"message": "Contrato desactivado"}
