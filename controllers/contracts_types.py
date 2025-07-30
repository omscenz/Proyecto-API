from fastapi import HTTPException
from bson import ObjectId
from models.contracts_types import ContractType
from utils.mongodb import get_collection

contracts_types_collection = get_collection("contracts_types")

async def create_contract_type(contract_type: ContractType):
    existing = await contracts_types_collection.find_one({
        "description": {
            "$regex": f"^{contract_type.description}$",
            "$options": "i"
        }
    })
    if existing:
        raise HTTPException(status_code=400, detail="Tipo de contrato ya existe")

    ct_dict = contract_type.model_dump(exclude_unset=True)
    result = await contracts_types_collection.insert_one(ct_dict)
    contract_type.id = str(result.inserted_id)
    return contract_type

async def list_contract_types(skip: int = 0, limit: int = 10):
    cursor = contracts_types_collection.find({"active": True}).skip(skip).limit(limit)
    contract_types = []
    async for ct in cursor:
        ct["id"] = str(ct["_id"])
        contract_types.append(ct)

    total = await contracts_types_collection.count_documents({"active": True})
    return {
        "contract_types": contract_types,
        "total": total,
        "skip": skip,
        "limit": limit
    }

async def get_contract_type_by_id(contract_type_id: str):
    if not ObjectId.is_valid(contract_type_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    ct = await contracts_types_collection.find_one({"_id": ObjectId(contract_type_id)})
    if not ct:
        raise HTTPException(status_code=404, detail="Tipo de contrato no encontrado")

    ct["id"] = str(ct["_id"])
    return ct

async def update_contract_type(contract_type_id: str, contract_type_data: dict):
    if not ObjectId.is_valid(contract_type_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    existing = await contracts_types_collection.find_one({
        "description": {
            "$regex": f"^{contract_type_data.get('description', '')}$",
            "$options": "i"
        },
        "_id": {"$ne": ObjectId(contract_type_id)}
    })
    if existing:
        raise HTTPException(status_code=400, detail="Tipo de contrato ya existe")

    result = await contracts_types_collection.update_one(
        {"_id": ObjectId(contract_type_id)},
        {"$set": contract_type_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tipo de contrato no encontrado")

    return {"message": "Tipo de contrato actualizado correctamente"}

async def disable_contract_type(contract_type_id: str):
    if not ObjectId.is_valid(contract_type_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    result = await contracts_types_collection.update_one(
        {"_id": ObjectId(contract_type_id)},
        {"$set": {"active": False}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tipo de contrato no encontrado")

    return {"message": "Tipo de contrato desactivado"}
