from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Importar TODOS los modelos para que se registren en el Base
from .categoria import Categoria
from .producto import Producto
from .pedido import Pedido
from .producto_pedido import ProductoPedido
from .sesion import Sesion
