"""WebSocket connection manager for real-time updates."""

import asyncio
import json
import logging
from collections import defaultdict

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections grouped by channel (run_id or user_id)."""

    def __init__(self):
        self._run_connections: dict[str, list[WebSocket]] = defaultdict(list)
        self._user_connections: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect_run(self, run_id: str, ws: WebSocket):
        await ws.accept()
        self._run_connections[run_id].append(ws)

    async def connect_user(self, user_id: int, ws: WebSocket):
        await ws.accept()
        self._user_connections[user_id].append(ws)

    def disconnect_run(self, run_id: str, ws: WebSocket):
        conns = self._run_connections.get(run_id, [])
        if ws in conns:
            conns.remove(ws)

    def disconnect_user(self, user_id: int, ws: WebSocket):
        conns = self._user_connections.get(user_id, [])
        if ws in conns:
            conns.remove(ws)

    async def broadcast_to_run(self, run_id: str, data: dict):
        message = json.dumps(data)
        dead = []
        for ws in self._run_connections.get(run_id, []):
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect_run(run_id, ws)

    async def broadcast_to_user(self, user_id: int, data: dict):
        message = json.dumps(data)
        dead = []
        for ws in self._user_connections.get(user_id, []):
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect_user(user_id, ws)

    async def keepalive(self, ws: WebSocket):
        """Send periodic pings to keep the connection alive."""
        try:
            while True:
                await asyncio.sleep(30)
                await ws.send_text(json.dumps({"type": "ping"}))
        except Exception:
            pass


manager = ConnectionManager()
