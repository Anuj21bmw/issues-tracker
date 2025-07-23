# backend/app/main.py - Updated with AI integration
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response, FileResponse
import structlog
import time
import os

from app.api.auth import router as auth_router
from app.api.issues import router as issues_router
from app.api.dashboard import router as dashboard_router
from app.api.ai import router as ai_router  # New AI router
from app.api.websocket import manager
from app.database import engine, Base
from app.core.config import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.dev.ConsoleRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Enhanced Issues & Insights Tracker API",
    description="A next-generation SaaS for intelligent issue tracking with AI capabilities",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware with production settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.railway_environment == "development" else settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for metrics and logging
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    
    logger.info("Request started", method=request.method, url=str(request.url))
    
    response = await call_next(request)
    process_time = time.time() - start_time
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(process_time)
    
    logger.info("Request completed", method=request.method, status_code=response.status_code, process_time=process_time)
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Mount static files
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Mount static frontend files if they exist
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(issues_router, prefix="/api/issues", tags=["issues"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(ai_router, prefix="/api/ai", tags=["ai"])  # New AI endpoints

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Health check with AI services
@app.get("/health")
async def health_check():
    health_data = {
        "status": "healthy", 
        "timestamp": time.time(), 
        "environment": settings.railway_environment,
        "services": {
            "database": "healthy",
            "ai_services": "healthy"
        }
    }
    
    # Check AI services health
    try:
        from app.ai.classifier import IssueClassifier
        classifier = IssueClassifier()
        # Simple test classification
        test_result = await classifier.classify_issue("Test", "Test description")
        health_data["services"]["ai_classifier"] = "healthy"
    except Exception as e:
        health_data["services"]["ai_classifier"] = f"unhealthy: {str(e)}"
        health_data["status"] = "degraded"
    
    return health_data

# Root endpoint - serve frontend in production
@app.get("/")
async def read_root():
    # In production, serve the built frontend
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    
    # In development, return API info with AI features
    return {
        "message": "AI-Enhanced Issues & Insights Tracker API", 
        "status": "running",
        "version": "2.0.0",
        "features": [
            "Intelligent issue classification",
            "AI-powered chat assistant", 
            "Predictive analytics",
            "Smart assignment suggestions",
            "Document processing with OCR",
            "Automated escalation detection"
        ],
        "docs": "/api/docs",
        "environment": settings.railway_environment
    }

# Catch-all route for SPA routing
@app.get("/{path:path}")
async def catch_all(path: str):
    # Serve static files if they exist
    if os.path.exists(f"static/{path}"):
        return FileResponse(f"static/{path}")
    
    # For SPA routes, serve index.html
    if os.path.exists("static/index.html") and not path.startswith("api/"):
        return FileResponse("static/index.html")
    
    # Return 404 for API routes or if no static files
    return {"error": "Not found"}, 404

@app.get("/api/demo")
def demo_endpoint():
    return {
        "demo_accounts": [
            {"role": "ADMIN", "email": "admin@example.com", "password": "admin123"},
            {"role": "MAINTAINER", "email": "maintainer@example.com", "password": "maintainer123"},
            {"role": "REPORTER", "email": "reporter@example.com", "password": "reporter123"}
        ],
        "ai_features": [
            "🤖 AI Chat Assistant - Ask questions in natural language",
            "🎯 Smart Classification - Automatic severity and tag suggestions", 
            "⏰ Time Prediction - AI estimates resolution time",
            "📊 Predictive Analytics - Forecast trends and bottlenecks",
            "🎪 Auto Assignment - AI suggests best assignee",
            "📱 Document Analysis - Extract insights from uploads",
            "🚨 Smart Notifications - Intelligent escalation alerts"
        ],
        "endpoints": {
            "docs": "/api/docs",
            "health": "/health",
            "auth": "/api/auth",
            "issues": "/api/issues", 
            "dashboard": "/api/dashboard",
            "ai": "/api/ai"
        },
        "environment": settings.railway_environment
    }