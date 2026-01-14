"""
WebSocket manager for real-time progress updates
Handles connections and broadcasts processing status
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio


class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        print(f"[WebSocket] Client connected: {session_id} ({len(self.active_connections[session_id])} connections)")
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """Remove WebSocket connection"""
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        print(f"[WebSocket] Client disconnected: {session_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific connection"""
        await websocket.send_text(json.dumps(message))
    
    async def broadcast_to_session(self, message: dict, session_id: str):
        """Broadcast message to all connections in a session"""
        if session_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)
            
            # Clean up disconnected clients
            for conn in disconnected:
                self.disconnect(conn, session_id)
    
    async def broadcast_all(self, message: dict):
        """Broadcast message to all connected clients"""
        for session_id in list(self.active_connections.keys()):
            await self.broadcast_to_session(message, session_id)


# Global connection manager instance
manager = ConnectionManager()


class ProgressTracker:
    """Tracks processing progress for real-time updates"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.steps = [
            {"name": "Vision Agent", "status": "pending", "progress": 0},
            {"name": "NLP Agent", "status": "pending", "progress": 0},
            {"name": "Fraud Agent", "status": "pending", "progress": 0},
            {"name": "Policy Agent", "status": "pending", "progress": 0},
            {"name": "Decision Agent", "status": "pending", "progress": 0},
        ]
        self.current_step = 0
        self.overall_progress = 0
    
    async def start_step(self, step_index: int):
        """Mark step as in-progress"""
        if 0 <= step_index < len(self.steps):
            self.steps[step_index]["status"] = "processing"
            self.steps[step_index]["progress"] = 50
            self.current_step = step_index
            self.overall_progress = (step_index / len(self.steps)) * 100
            await self._send_update()
    
    async def complete_step(self, step_index: int, result: dict = None):
        """Mark step as complete"""
        if 0 <= step_index < len(self.steps):
            self.steps[step_index]["status"] = "complete"
            self.steps[step_index]["progress"] = 100
            if result:
                self.steps[step_index]["result"] = result
            self.overall_progress = ((step_index + 1) / len(self.steps)) * 100
            await self._send_update()
    
    async def fail_step(self, step_index: int, error: str):
        """Mark step as failed"""
        if 0 <= step_index < len(self.steps):
            self.steps[step_index]["status"] = "error"
            self.steps[step_index]["error"] = error
            await self._send_update()
    
    async def _send_update(self):
        """Send progress update via WebSocket"""
        message = {
            "type": "progress",
            "session_id": self.session_id,
            "steps": self.steps,
            "current_step": self.current_step,
            "overall_progress": self.overall_progress
        }
        await manager.broadcast_to_session(message, self.session_id)
