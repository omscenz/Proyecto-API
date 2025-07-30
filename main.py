
import sys
import os
sys.path.append(os.path.dirname(__file__))


import uvicorn
import logging

from fastapi import FastAPI, Request
from dotenv import load_dotenv
from fastapi import FastAPI



# Cargar variables de entorno
load_dotenv()

# Importar controladores para login y registro
from controllers.users import create_user, login
from models.users import User
from models.login import Login

# Middleware personalizado
from utils.security import validateuser, validateadmin

# Importar routers
from routes.contracts_types import router as type_contracts_router
from routes.games import router as games_router
from routes.developers import router as developers_router
from routes.contracts import router as contracts_router
from routes.wishlist import router as wishlists_router
from routes.purchases import router as purchases_router
from routes.rewards import router as rewards_router
from routes.users import router as users_router



# Inicializar app
app = FastAPI()

# Registrar routers
app.include_router(type_contracts_router)
app.include_router(games_router)
app.include_router(developers_router)
app.include_router(contracts_router)
app.include_router(wishlists_router)
app.include_router(purchases_router)
app.include_router(rewards_router)
app.include_router(users_router, tags=["Users"])

# Logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
def read_root():
    return {"version": "1.0.0", "message": "API Tienda de Videojuegos"}

@app.post("/users")
async def create_user_endpoint(user: User) -> User:
    return await create_user(user)

@app.post("/login")
async def login_endpoint(login_data: Login) -> dict:
    return await login(login_data)

@app.get("/exampleadmin")
@validateadmin
async def protected_admin(request: Request):
    return {
        "message": "Este es un endpoint protegido para administradores",
        "admin": request.state.admin
    }

@app.get("/exampleuser")
@validateuser
async def protected_user(request: Request):
    return {
        "message": "Este es un endpoint protegido para usuarios",
        "email": request.state.email
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
