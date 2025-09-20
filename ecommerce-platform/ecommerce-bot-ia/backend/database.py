from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ecommerce.db")

# Convert sync URL to async URL
ASYNC_DATABASE_URL = SQLALCHEMY_DATABASE_URL
if "sqlite:" in SQLALCHEMY_DATABASE_URL:
    ASYNC_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("sqlite:", "sqlite+aiosqlite:")
elif "postgresql:" in SQLALCHEMY_DATABASE_URL:
    ASYNC_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql:", "postgresql+asyncpg:")

# Sync engine (para Alembic migrations)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

# Async engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in ASYNC_DATABASE_URL else {},
    echo=False  # Set to True for debugging SQL queries
)

# Sync sessionmaker (para compatibility)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async sessionmaker
AsyncSessionLocal = async_sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

# Sync dependency (legacy compatibility)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Async dependency
async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()