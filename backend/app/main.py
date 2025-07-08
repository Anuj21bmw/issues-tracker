from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST
from starlette.responses import Response
import structlog
import time
import os

from app.api.auth import router as auth_router
from app.api.issues import router as issues_router
from app.api.dashboard import router as dashboard_router
from app.api.websocket import ConnectionManager
from app.database import engine, Base
from app.models import User, Issue, DailyStats
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
    title="Issues & Insights Tracker",
    description="A mini SaaS for tracking issues and insights",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager
manager = ConnectionManager()

# Middleware for metrics and logging
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host
    )
    
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Update metrics
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(process_time)
    
    # Log response
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Mount static files
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(issues_router, prefix="/api/issues", tags=["issues"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle any incoming WebSocket messages if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)