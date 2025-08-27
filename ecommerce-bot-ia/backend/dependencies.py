from typing import Generator
from sqlalchemy.orm import Session
from database import SessionLocal

def get_db() -> Generator:
    """
    Database dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication dependencies could be added here in the future
# def get_current_user():
#     pass

# def verify_token():
#     pass