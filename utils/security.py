import os
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from jwt import PyJWTError
from functools import wraps

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
print("SECRET_KEY:", SECRET_KEY)
security = HTTPBearer()

def create_jwt_token(
        name_profile: str,
        email: str,
        active: bool,
        admin: bool,
        user_id: str
    ) -> str:
    expiration = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode(
        {
            "id": user_id,
            "name_profile": name_profile,
            "email": email,
            "active": active,
            "admin": admin,
            "exp": expiration,
            "iat": datetime.utcnow()
        },
        SECRET_KEY,
        algorithm="HS256"
    )
    return token

def validateuser(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get('request')
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found")

        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=400, detail="Authorization header missing")

        try:
            schema, token = authorization.split()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Authorization header format")

        if schema.lower() != "bearer":
            raise HTTPException(status_code=400, detail="Invalid auth schema")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            email = payload.get("email")
            name_profile = payload.get("name_profile")
            active = payload.get("active")
            exp = payload.get("exp")
            user_id = payload.get("id")

            if email is None:
                raise HTTPException(status_code=401, detail="Invalid token")

            if datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Expired token")

            if not active:
                raise HTTPException(status_code=401, detail="Inactive user")

            # Attach to request state for use in endpoint
            request.state.email = email
            request.state.name_profile = name_profile
            request.state.id = user_id

        except PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        return await func(*args, **kwargs)
    return wrapper

def validateadmin(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get('request')
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found")

        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=400, detail="Authorization header missing")

        try:
            schema, token = authorization.split()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Authorization header format")

        if schema.lower() != "bearer":
            raise HTTPException(status_code=400, detail="Invalid auth schema")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            email = payload.get("email")
            name_profile = payload.get("name_profile")
            active = payload.get("active")
            admin = payload.get("admin")
            exp = payload.get("exp")
            user_id = payload.get("id")

            if email is None:
                raise HTTPException(status_code=401, detail="Invalid token")

            if datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Expired token")

            if not active or not admin:
                raise HTTPException(status_code=401, detail="Inactive user or not admin")

            request.state.email = email
            request.state.name_profile = name_profile
            request.state.admin = admin
            request.state.id = user_id

        except PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        return await func(*args, **kwargs)
    return wrapper

# FastAPI Dependency Injection versions for use with Depends()
def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        email = payload.get("email")
        name_profile = payload.get("name_profile")
        active = payload.get("active")
        admin = payload.get("admin", False)
        exp = payload.get("exp")
        user_id = payload.get("id")

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        if datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Expired token")

        if not active:
            raise HTTPException(status_code=401, detail="Inactive user")

        return {
            "id": user_id,
            "email": email,
            "name_profile": name_profile,
            "active": active,
            "role": "admin" if admin else "user"
        }

    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def validate_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        email = payload.get("email")
        name_profile = payload.get("name_profile")
        active = payload.get("active")
        admin = payload.get("admin", False)
        exp = payload.get("exp")
        user_id = payload.get("id")

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        if datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Expired token")

        if not active or not admin:
            raise HTTPException(status_code=401, detail="Inactive user or not admin")

        return {
            "id": user_id,
            "email": email,
            "name_profile": name_profile,
            "active": active,
            "role": "admin"
        }

    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

__all__ = ["create_jwt_token", "decode_jwt_token", "validate_token", "validate_admin"]
