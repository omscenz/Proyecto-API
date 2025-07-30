from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

DB = os.getenv("MONGO_DB_NAME")
URI = os.getenv("URI")

# Conectar a MongoDB con cliente asíncrono
client = AsyncIOMotorClient(URI)
db = client[DB]

# Función para obtener una colección
def get_collection(name):
    return db[name]
