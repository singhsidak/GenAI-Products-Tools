"""FastAPI application entry point."""

import asyncio
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .auth import hash_password
from .database import init_db, SessionLocal
from .models import User
from .routes import auth, runs, sections, compliance, admin, dashboard
from .websocket import manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(title="CSR Generation API", version="1.0.0")

# CORS — allow Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST routes under /api
app.include_router(auth.router, prefix="/api")
app.include_router(runs.router, prefix="/api")
app.include_router(sections.router, prefix="/api")
app.include_router(compliance.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


# ── WebSocket endpoints ───────────────────────────────────────────────────────

@app.websocket("/ws/run/{run_id}")
async def ws_run(websocket: WebSocket, run_id: str):
    await manager.connect_run(run_id, websocket)
    ping_task = asyncio.create_task(manager.keepalive(websocket))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        ping_task.cancel()
        manager.disconnect_run(run_id, websocket)


@app.websocket("/ws/user/{user_id}")
async def ws_user(websocket: WebSocket, user_id: int):
    await manager.connect_user(user_id, websocket)
    ping_task = asyncio.create_task(manager.keepalive(websocket))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        ping_task.cancel()
        manager.disconnect_user(user_id, websocket)


# ── Startup ───────────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    init_db()
    _seed_admin()


def _seed_admin():
    """Create default admin user if none exists."""
    db = SessionLocal()
    try:
        if db.query(User).filter(User.role == "admin").first():
            return
        admin_user = User(
            username="admin",
            email="admin@csr-gen.local",
            full_name="System Administrator",
            hashed_password=hash_password("admin123"),
            role="admin",
            is_active=True,
            force_password_change=True,
        )
        db.add(admin_user)
        db.commit()
        logging.getLogger(__name__).info("Seeded default admin user (admin / admin123)")
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {"status": "ok"}
