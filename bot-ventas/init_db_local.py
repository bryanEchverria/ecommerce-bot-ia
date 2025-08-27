import os
from sqlalchemy.orm import Session
from core.db import engine, SessionLocal
from models import Base
from models.categoria import Categoria
from models.producto import Producto
from models.pedido import Pedido
from models.producto_pedido import ProductoPedido

print("🔄 Inicializando base de datos local...")

# 1️⃣ Borrar base de datos local si existe (opcional)
if os.path.exists("whatsapp_bot.db"):
    os.remove("whatsapp_bot.db")

# 2️⃣ Crear todas las tablas
Base.metadata.create_all(bind=engine)

# 3️⃣ Insertar datos de ejemplo
db: Session = SessionLocal()

# Categorías
cat1 = Categoria(nombre="Panadería", orden=1)
cat2 = Categoria(nombre="Bebidas", orden=2)
db.add_all([cat1, cat2])
db.flush()

# Productos
prod1 = Producto(nombre="Pan", precio=1000, categoria_id=cat1.id)
prod2 = Producto(nombre="Bebida", precio=1500, categoria_id=cat2.id)
db.add_all([prod1, prod2])

# Pedido de ejemplo
pedido1 = Pedido(monto_total=3500, estado="pendiente_pago")
db.add(pedido1)
db.flush()

# Relación productos_pedidos
rel1 = ProductoPedido(pedido_id=pedido1.id, producto_id=prod1.id, cantidad=2)
rel2 = ProductoPedido(pedido_id=pedido1.id, producto_id=prod2.id, cantidad=1)
db.add_all([rel1, rel2])

db.commit()
db.close()

print("✅ Base de datos local creada con datos de ejemplo")
