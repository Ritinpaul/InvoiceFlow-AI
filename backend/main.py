from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from backend.api.router import router
from backend.database import init_db, seed_vendors, SessionLocal
from contextlib import asynccontextmanager
import traceback

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    print("Starting InvoiceFlow AI Backend...")
    try:
        init_db()
        # Seed vendors
        db = SessionLocal()
        try:
            seed_vendors(db)
        finally:
            db.close()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"⚠ Database initialization warning: {e}")
    
    yield
    
    # Shutdown
    print("Shutting down InvoiceFlow AI Backend...")

app = FastAPI(
    title="InvoiceFlow AI",
    description="Multi-Agent Invoice Processing System",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Validation error",
            "details": exc.errors(),
            "body": str(exc.body) if hasattr(exc, 'body') else None
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors gracefully"""
    error_trace = traceback.format_exc()
    print(f"❌ Unexpected error: {error_trace}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "An unexpected error occurred",
            "error": str(exc),
            "type": type(exc).__name__
        }
    )

@app.get("/")
def read_root():
    return {
        "message": "InvoiceFlow AI Backend is running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "InvoiceFlow AI",
        "agents": {
            "vision": "ready",
            "nlp": "ready",
            "fraud": "ready",
            "policy": "ready",
            "decision": "ready"
        }
    }

