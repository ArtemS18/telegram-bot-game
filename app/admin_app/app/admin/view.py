from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from .schemes import TokenResponse
import jwt


class AdminView:
    def __init__(self, app):
        self.app = app
        self.router = APIRouter(prefix="/admin", tags=["Admin Auth"])
        self.router.add_api_route(
            "/login", self.login,
            methods=["POST"],
            response_model=TokenResponse
        )

    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        jwt_config = self.app.config.jwt
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=jwt_config.access_tokem_expire_minutes))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, jwt_config.secret_key, algorithm=jwt_config.algorithm)
        return encoded_jwt

    async def login(self, form_data: OAuth2PasswordRequestForm = Depends()):
        admin_config = self.app.config.admin 
        if form_data.username != admin_config.email or form_data.password != admin_config.password:
            raise HTTPException(status_code=401, detail="Incorrect credentials")
        access_token = self.create_access_token({"sub": admin_config.email})
        return {"access_token": access_token, "token_type": "bearer"}

    def get_router(self):
        return self.router