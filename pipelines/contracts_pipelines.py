#Pipeline 1 Agregación con Lookup (Requerido): Endpoint que una
#información de múltiples colecciones usando $lookup para enriquecer la
#respuesta


def get_contracts_with_details_pipeline(skip: int = 0, limit: int = 10):
    return [
        {"$match": {"active": True}},
        {"$skip": skip},
        {"$limit": limit},
        # Convertir developer_id, game_id y type_contract_id a ObjectId
        {"$addFields": {
            "developer_obj_id": {"$toObjectId": "$developer_id"},
            "game_obj_id": {"$toObjectId": "$game_id"},
            "type_contract_obj_id": {"$toObjectId": "$type_contract_id"},
        }},
        # Lookup developer
        {"$lookup": {
            "from": "developers",
            "localField": "developer_obj_id",
            "foreignField": "_id",
            "as": "developer_info"
        }},
        {"$unwind": "$developer_info"},
        # Lookup game
        {"$lookup": {
            "from": "games",
            "localField": "game_obj_id",
            "foreignField": "_id",
            "as": "game_info"
        }},
        {"$unwind": "$game_info"},
        # Lookup contract type
        {"$lookup": {
            "from": "contract_types",
            "localField": "type_contract_obj_id",
            "foreignField": "_id",
            "as": "type_contract_info"
        }},
        {"$unwind": "$type_contract_info"},
        # Proyección limpia (excluir ObjectId internos)
        {"$project": {
            "_id": 1,
            "developer_id": 1,
            "game_id": 1,
            "type_contract_id": 1,
            "start_date": 1,
            "end_date": 1,
            "active": 1,
            "developer_info.id": {"$toString": "$developer_info._id"},
            "developer_info.name": 1,
            "game_info.id": {"$toString": "$game_info._id"},
            "game_info.title": 1,
            "type_contract_info.id": {"$toString": "$type_contract_info._id"},
            "type_contract_info.description": 1
        }}
    ]

def count_contracts_pipeline():
    return [
        {"$match": {"active": True}},
        {"$count": "total"}
    ]

#Un developer no puede tener dos contratos activos para el mismo juego al mismo tiempo.
#Pipeline 3 Validación Compleja (Requerido): Endpoint que use pipelines para
#validar reglas de negocio complejas antes de realizar operaciones


def check_existing_active_contract_pipelines(developer_id: str, game_id: str):
    return [
        {
            "$match": {
                "developer_id": developer_id,
                "game_id": game_id,
                "active": True
            }
        },
        {
            "$count": "existing_contracts"
        }
    ]
