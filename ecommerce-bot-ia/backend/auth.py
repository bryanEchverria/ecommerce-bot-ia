from datetime import datetime, timedelta
from typing import Optional, Union
import os
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from auth_models import TenantUser, TenantClient

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALG", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TTL_MIN", "120"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TTL_DAYS", "7"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

class TenantService:
    @staticmethod
    def get_user_by_email(db: Session, email: str, client_id: str) -> Optional[TenantUser]:
        return db.query(TenantUser).filter(
            TenantUser.email == email,
            TenantUser.client_id == client_id
        ).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[TenantUser]:
        return db.query(TenantUser).filter(TenantUser.id == user_id).first()
    
    @staticmethod
    def get_client_by_slug(db: Session, slug: str) -> Optional[TenantClient]:
        return db.query(TenantClient).filter(TenantClient.slug == slug).first()
    
    @staticmethod
    def get_client_by_id(db: Session, client_id: str) -> Optional[TenantClient]:
        return db.query(TenantClient).filter(TenantClient.id == client_id).first()
    
    @staticmethod
    def create_client(db: Session, name: str, slug: str) -> TenantClient:
        db_client = TenantClient(name=name, slug=slug)
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        return db_client
    
    @staticmethod
    def create_user(db: Session, email: str, password: str, client_id: str, role: str = "user") -> TenantUser:
        hashed_password = AuthService.get_password_hash(password)
        db_user = TenantUser(
            email=email,
            password_hash=hashed_password,
            client_id=client_id,
            role=role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

def get_current_user_and_client(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    request: Request = None
) -> tuple[TenantUser, TenantClient]:
    """
    Dependency que extrae y valida el usuario y client del JWT token.
    También valida opcionalmente el header X-Client-Slug.
    """
    token = credentials.credentials
    payload = AuthService.verify_token(token)
    
    user_id: str = payload.get("sub")
    client_id: str = payload.get("client_id")
    
    if user_id is None or client_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = TenantService.get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    client = TenantService.get_client_by_id(db, client_id)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Client not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validar header X-Client-Slug si está presente
    if request and "x-client-slug" in request.headers:
        client_slug_header = request.headers["x-client-slug"]
        if client_slug_header != client.slug:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client slug mismatch"
            )
    
    return user, client

def get_current_user(
    user_and_client: tuple[TenantUser, TenantClient] = Depends(get_current_user_and_client)
) -> TenantUser:
    """Convenience dependency para obtener solo el usuario."""
    user, _ = user_and_client
    return user

def get_current_client(
    user_and_client: tuple[TenantUser, TenantClient] = Depends(get_current_user_and_client)
) -> TenantClient:
    """Convenience dependency para obtener solo el client."""
    _, client = user_and_client
    return client

def tenant_filter_query(query, model, client_id: str):
    """Helper para filtrar queries automáticamente por client_id."""
    if hasattr(model, 'client_id'):
        return query.filter(model.client_id == client_id)
    return query