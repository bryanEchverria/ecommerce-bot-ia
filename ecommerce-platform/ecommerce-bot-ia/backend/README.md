# Backend - E-commerce Backoffice API

API FastAPI para el sistema de gestión de e-commerce.

## Inicio Rápido

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python main.py
```

El servidor estará disponible en: http://127.0.0.1:8000

## API Documentation

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Estructura

```
backend/
├── routers/            # Endpoints de la API
│   ├── products.py     # CRUD de productos
│   ├── campaigns.py    # CRUD de campañas
│   ├── discounts.py    # CRUD de descuentos
│   ├── orders.py       # CRUD de pedidos
│   ├── clients.py      # CRUD de clientes
│   ├── dashboard.py    # Estadísticas
│   └── assistant.py    # Asistente IA
├── main.py            # Punto de entrada
├── models.py          # Modelos SQLAlchemy
├── schemas.py         # Schemas Pydantic
├── crud.py           # Operaciones CRUD
├── database.py       # Configuración BD
└── ecommerce.db      # Base de datos SQLite
```

## Endpoints Principales

### Productos
- `GET /api/products` - Listar productos
- `POST /api/products` - Crear producto
- `PUT /api/products/{id}` - Actualizar producto
- `DELETE /api/products/{id}` - Eliminar producto

### Campañas
- `GET /api/campaigns` - Listar campañas
- `POST /api/campaigns` - Crear campaña
- `PUT /api/campaigns/{id}` - Actualizar campaña
- `DELETE /api/campaigns/{id}` - Eliminar campaña

### Descuentos
- `GET /api/discounts` - Listar descuentos
- `POST /api/discounts` - Crear descuento
- `PUT /api/discounts/{id}` - Actualizar descuento
- `DELETE /api/discounts/{id}` - Eliminar descuento

### Dashboard
- `GET /api/dashboard/stats` - Estadísticas generales
- `GET /api/dashboard/recent-orders` - Pedidos recientes
- `GET /api/dashboard/low-stock-products` - Productos con bajo stock

## Tecnologías

- **FastAPI** - Framework web moderno
- **SQLAlchemy** - ORM
- **SQLite** - Base de datos (desarrollo)
- **Pydantic** - Validación de datos
- **Uvicorn** - Servidor ASGI