"""
SentinelOps API - Decision Intelligence for DevOps
Author: Arsh Verma
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
"""
Database Configuration
Author: Arsh Verma
"""
from contextlib import asynccontextmanager
from app.database import create_tables
from app.routers import webhooks, repositories, pull_requests, incidents, dashboard, analysis, simulation
from app.services.websocket_service import manager
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to specific domains in production (e.g., localhost:3000)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
