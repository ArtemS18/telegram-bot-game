from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt


class AdminAuth:
    def __init__(self, app):
        self.app = app
       
    def get_current_admin(self, token: str = Depends(OAuth2PasswordBearer(tokenUrl="/admin/login"))):
        try:
            config = self.app.config.jwt
            payload = jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
            admin_email = payload.get("sub")
            if not admin_email:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
            return admin_email
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        
