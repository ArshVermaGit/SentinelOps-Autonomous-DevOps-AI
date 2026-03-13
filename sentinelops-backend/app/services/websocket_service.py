"""
WebSocket service for real-time dashboard updates.
"""

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)

        for conn in dead:
            self.disconnect(conn)


manager = ConnectionManager()


async def broadcast_new_incident(incident_id: int):
    await manager.broadcast(
        {
            "type": "new_incident",
            "incident_id": incident_id,
            "message": f"New incident detected: #{incident_id}",
        }
    )


async def broadcast_ci_failure(ci_run_id: int, repo_name: str):
    await manager.broadcast(
        {
            "type": "ci_failure",
            "ci_run_id": ci_run_id,
            "repo_name": repo_name,
            "message": f"CI failure detected in {repo_name}",
        }
    )


async def broadcast_pr_risk(pr_id: int, risk_level: str, risk_probability: float):
    await manager.broadcast(
        {
            "type": "pr_risk_update",
            "pr_id": pr_id,
            "risk_level": risk_level,
            "risk_probability": risk_probability,
        }
    )
