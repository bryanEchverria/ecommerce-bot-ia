from database import get_db
from models import FlowProduct

# Crear producto iPhone para Sintestesia
db = next(get_db())
try:
    # Verificar si ya existe
    existing = db.query(FlowProduct).filter_by(nombre='iPhone 15 Pro', client_id='2ae13937-cbaa-45c5-b7bc-9c73586483de').first()
    if not existing:
        iphone = FlowProduct(
            nombre='iPhone 15 Pro',
            descripcion='iPhone 15 Pro 128GB con chip A17 Pro',
            precio=1199000,
            client_id='2ae13937-cbaa-45c5-b7bc-9c73586483de'
        )
        db.add(iphone)
        db.commit()
        print('iPhone 15 Pro agregado para cliente Sintestesia')
    else:
        print('iPhone 15 Pro ya existe')
        
    # Mostrar productos existentes
    productos = db.query(FlowProduct).filter_by(client_id='2ae13937-cbaa-45c5-b7bc-9c73586483de').all()
    print(f'Productos disponibles para Sintestesia: {len(productos)}')
    for p in productos:
        print(f'  - {p.nombre}: ${p.precio}')
        
except Exception as e:
    print(f'Error: {e}')