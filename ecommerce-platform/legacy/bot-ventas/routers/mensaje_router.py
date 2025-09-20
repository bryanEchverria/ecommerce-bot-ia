from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.db import get_db
from schemas.mensaje_schema import MensajeEntrada
from services import chat_service

router = APIRouter(tags=["Mensajes"])

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from core.db import get_db
from services import chat_service

router = APIRouter(tags=["Mensajes"])

# Esquema de entrada
class MensajeEntrada(BaseModel):
    telefono: str
    mensaje: str


@router.post("/mensaje")    
def recibir_mensaje(data: MensajeEntrada, db: Session = Depends(get_db)):
    """
    Endpoint que procesa un mensaje entrante desde Twilio/n8n
    """
    respuesta = chat_service.procesar_mensaje(db, data.telefono, data.mensaje)
    return {"respuesta": respuesta}
