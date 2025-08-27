from sqlalchemy import Column, Integer, Float, String, DateTime, func
from models import Base

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=func.now())
    monto_total = Column(Float, nullable=False)

    # Estado: pendiente_pago, pagado, cancelado
    estado = Column(String(20), default="pendiente_pago", nullable=False)

    # Nuevo campo: token del pago Flow
    token = Column(String(255), nullable=True)
