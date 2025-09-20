from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from . import Base  # Importamos el Base centralizado

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)
    precio = Column(Numeric(10, 2), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    stock = Column(Integer, default=0)
    disponible = Column(Boolean, default=True)
    activo = Column(Boolean, default=True)

    categoria = relationship("Categoria", backref="productos")
