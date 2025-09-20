from sqlalchemy import Column, String, JSON, DateTime
from . import Base
from datetime import datetime

class Sesion(Base):
    __tablename__ = "sesiones"

    telefono = Column(String, primary_key=True, index=True)
    estado = Column(String, nullable=False)  # ❌ Sin ForeignKey
    subestado = Column(String, nullable=True)
    datos = Column(JSON, nullable=True)
    actualizado_en = Column(DateTime, default=datetime.utcnow)
