import os
import logging
import firebase_admin
import requests
from fastapi import HTTPException
from firebase_admin import credentials, auth as firebase_auth
from bson import ObjectId
from fastapi import status

from models.users import User
from models.login import Login

from utils.security import create_jwt_token
from utils.mongodb import get_collection

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Firebase si no está ya inicializado
if not firebase_admin._apps:
    print("Ruta absoluta actual:", os.getcwd())
    print("Archivos en 'secrets/':", os.listdir("secrets"))
    ruta_absoluta = os.path.join(os.getcwd(), "secrets", "tienda_secret.json")
    cred = credentials.Certificate(ruta_absoluta)
    firebase_admin.initialize_app(cred)

# Crear usuario nuevo
async def create_user(user: User) -> User:
    try:
        user_record = firebase_auth.create_user(
            email=user.email,
            password=user.password
        )
    except Exception as e:
        logger.warning(e)
        raise HTTPException(
            status_code=400,
            detail="Error al registrar usuario en Firebase"
        )

    try:
        coll = get_collection("users")

        new_user = User(
            name=user.name,
            lastname=user.lastname,
            email=user.email,
            password=user.password
        )

        user_dict = new_user.model_dump(exclude={"id", "password"})
        inserted = coll.insert_one(user_dict)
        new_user.id = str(inserted.inserted_id)
        new_user.password = "*********"  # Enmascarar

        return new_user

    except Exception as e:
        firebase_auth.delete_user(user_record.uid)
        logger.error(f"Error creando usuario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en base de datos: {str(e)}")

# Login
async def login(user: Login) -> dict:
    api_key = os.getenv("FIREBASE_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="FIREBASE_API_KEY no está definida en las variables de entorno"
        )

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": user.email,
        "password": user.password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)

    try:
        response_data = response.json()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado al procesar respuesta de Firebase: {e}"
        )

    if "error" in response_data:
        raise HTTPException(
            status_code=400,
            detail="Error al autenticar usuario"
        )

    coll = get_collection("users")
    user_info = coll.find_one({"email": user.email})

    if not user_info:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado en la base de datos"
        )

    return {
        "message": "Usuario autenticado correctamente",
        "idToken": create_jwt_token(
            user_info["name"],
            user_info["lastname"],
            user_info["email"],
            user_info["active"],
            user_info["admin"],
            str(user_info["_id"])
        )
    }

# Listar todos los usuarios
async def list_users():
    coll = get_collection("users")
    users_cursor = coll.find()
    users = []
    for doc in users_cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        doc.pop("password", None)
        users.append(doc)
    return users

# Obtener un usuario por ID
async def get_user_by_id(user_id: str):
    coll = get_collection("users")
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    doc = coll.find_one({"_id": ObjectId(user_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    doc.pop("password", None)
    return doc

# Actualizar usuario
async def update_user(user_id: str, user: User):
    coll = get_collection("users")
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    update_data = user.model_dump(exclude_unset=True, exclude={"id", "password"})
    result = coll.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    updated_doc = coll.find_one({"_id": ObjectId(user_id)})
    updated_doc["id"] = str(updated_doc["_id"])
    updated_doc.pop("_id", None)
    updated_doc.pop("password", None)
    return updated_doc

# Desactivar usuario (soft delete)
async def deactivate_user(user_id: str) -> dict:
    coll = get_collection("users")
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    result = coll.update_one({"_id": ObjectId(user_id)}, {"$set": {"active": False}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {"message": "Usuario desactivado correctamente"}
