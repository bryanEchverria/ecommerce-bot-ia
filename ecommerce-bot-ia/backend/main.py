from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from database import engine, Base
from routers import products, orders, clients, dashboard, assistant
from routers.campaigns import router as campaigns_router
from routers.discounts import router as discounts_router
from routers.bot import router as bot_router
from routers.auth import router as auth_router
from routers.tenant_orders import router as tenant_orders_router
from routers.twilio_webhook import router as twilio_router
from routers.flow_router import router as flow_router
from routers.flow_orders import router as flow_orders_router
from routers.whatsapp_settings import router as whatsapp_settings_router
from routers.debug import router as debug_router
from tenant_middleware import TenantMiddleware

app = FastAPI(
    title="E-commerce Backoffice API",
    description="API for e-commerce backoffice management with multi-tenant authentication",
    version="2.0.0"
)

# Register tenant middleware FIRST (before any other middleware)
app.add_middleware(TenantMiddleware)

# Startup event para inicializar servicios en background
@app.on_event("startup")
async def startup_event():
    """Inicializa servicios en background al arrancar la aplicación"""
    try:
        from services.timeout_service import start_timeout_service
        start_timeout_service()
        print("✅ Background services initialized")
    except Exception as e:
        print(f"⚠️ Warning: Could not start background services: {e}")

# Custom middleware to handle problematic API paths and reduce error notifications
@app.middleware("http")
async def fix_problematic_api_paths(request: Request, call_next):
    """
    Middleware to handle common frontend API path issues:
    1. Fix duplicate /api/api/ paths
    2. Redirect legacy /api/orders to tenant-aware endpoint
    3. Return proper errors for invalid paths to reduce noise
    """
    path = request.url.path
    print(f"Middleware processing path: {path}")  # Debug log
    
    # Fix duplicate /api/api/ prefix - redirect to correct path
    if "/api/api/" in path:
        new_path = path.replace("/api/api/", "/api/")
        new_url = str(request.url).replace(path, new_path)
        print(f"Redirecting {path} to {new_path}")  # Debug log
        return RedirectResponse(url=new_url, status_code=301)
    
    # Handle legacy /api/orders requests for GET method
    if path == "/api/orders" and request.method == "GET":
        print(f"Handling legacy orders endpoint")  # Debug log
        # Check if user has valid authentication for tenant-orders
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # Redirect to tenant-orders with 307 to preserve method and headers
            new_url = str(request.url).replace("/api/orders", "/api/tenant-orders/")
            return RedirectResponse(url=new_url, status_code=307)
        else:
            # Return a more informative error for missing auth
            return Response(
                content='{"detail":"Authentication required. Please use /api/tenant-orders/ with valid Bearer token."}',
                status_code=401,
                media_type="application/json"
            )
    
    # Continue with normal request processing
    response = await call_next(request)
    return response

# Tenant middleware is already registered above

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://app.sintestesia.cl",  # Production frontend
        "https://sintestesia.cl",      # Main domain
        "https://acme.sintestesia.cl", # ACME tenant frontend
        "https://bravo.sintestesia.cl", # Bravo tenant frontend
        "https://*.sintestesia.cl",    # Wildcard for all subdomains
    ],
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

# Bot endpoints (no prefix for webhook access - tenant-aware)
app.include_router(bot_router, tags=["bot"])

# Twilio webhook routes (no prefix for direct webhook access)
app.include_router(twilio_router, tags=["twilio"])

# Flow payment integration endpoints (no prefix for direct webhook access)
app.include_router(flow_router, tags=["flow"])

# Flow orders management endpoints for backoffice
app.include_router(flow_orders_router, prefix="/api", tags=["flow-orders"])

# WhatsApp settings management endpoints
app.include_router(whatsapp_settings_router, prefix="/api", tags=["whatsapp-settings"])

# Debug endpoints (only for development/testing)
app.include_router(debug_router, tags=["debug"])

@app.get("/")
async def root():
    return {"message": "E-commerce Backoffice API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)