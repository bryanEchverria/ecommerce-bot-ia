from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import products, orders, clients, dashboard, assistant
from routers.campaigns import router as campaigns_router
from routers.discounts import router as discounts_router
from routers.bot import router as bot_router
from routers.auth import router as auth_router
from routers.tenant_orders import router as tenant_orders_router

app = FastAPI(
    title="E-commerce Backoffice API",
    description="API for e-commerce backoffice management with multi-tenant authentication",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  # Enable credentials for JWT tokens
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# Auth routes (no prefix)
app.include_router(auth_router)

# Tenant-aware routes
app.include_router(tenant_orders_router, prefix="/api")

# Existing routes (legacy)
app.include_router(products.router, prefix="/api", tags=["products"])
app.include_router(orders.router, prefix="/api", tags=["orders"])
app.include_router(clients.router, prefix="/api", tags=["clients"])
app.include_router(campaigns_router, prefix="/api", tags=["campaigns"])
app.include_router(discounts_router, prefix="/api", tags=["discounts"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(assistant.router, prefix="/api", tags=["assistant"])
app.include_router(bot_router, prefix="/api", tags=["bot"])

@app.get("/")
async def root():
    return {"message": "E-commerce Backoffice API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)