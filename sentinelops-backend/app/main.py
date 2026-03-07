"""
SentinelOps API - Decision Intelligence for DevOps
Author: Arsh Verma
"""
from contextlib import asynccontextmanager
import logging
import traceback

import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import create_tables
from app.routers import (
    analysis,
    analytics_advanced,
    dashboard,
    incidents,
    local_dev,
    pull_requests,
    repositories,
    simulation,
    webhooks,
)
from app.routers import settings as settings_router
from app.services.websocket_service import manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        logger.error(traceback.format_exc())
    yield

app = FastAPI(
    title="SentinelOps API",
    description="""
🚀 **Autonomous DevOps AI Co-Pilot**
Engineering decision intelligence. Detect failures before they impact production.

### Key Capabilities:
* **Predictive Analysis** - ML-based PR risk scoring.
* **Root Cause Identification** - LLM-powered failure explanation.
* **Self-Healing Simulation** - Sandbox fix testing.
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred.",
            "type": exc.__class__.__name__
        }
    )

# Configurable CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(repositories.router, prefix="/api/repositories", tags=["Repositories"])
app.include_router(pull_requests.router, prefix="/api/pull-requests", tags=["Pull Requests"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["Incidents"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["Settings"])
app.include_router(analytics_advanced.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(local_dev.router, prefix="/api/local", tags=["Local Dev"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "SentinelOps"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, handle client messages
            data = await websocket.receive_text()
            # Echo back ping/pong for keepalive
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
