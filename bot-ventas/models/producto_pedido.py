from sqlalchemy import Column, Integer, ForeignKey
from . import Base  # Importamos el Base centralizado

class ProductoPedido(Base):
    __tablename__ = "productos_pedidos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id", ondelete="CASCADE"))
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"))
    cantidad = Column(Integer, nullable=False)
