import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.database import init_db, seed_db
from backend.routes.events import router as events_router
from backend.routes.memory import router as memory_router
from backend.routes.routine import router as routine_router
from backend.routes.privacy import router as privacy_router
from backend.routes.demo import router as demo_router
from backend.routes.vision_stream import router as vision_router

# Initialize Database on startup
init_db()
seed_db()

app = FastAPI(
    title="MemoryBridge AI",
    description="An External Memory System for Independent Living — The environment remembers, so they don't have to.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(events_router)
app.include_router(memory_router)
app.include_router(routine_router)
app.include_router(privacy_router)
app.include_router(demo_router)
app.include_router(vision_router)

# Mount Frontend static assets
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

if os.path.exists(frontend_dir):
    # Route main pages explicitly for clean URLs
    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(frontend_dir, "index.html"))

    @app.get("/replay")
    def serve_replay():
        return FileResponse(os.path.join(frontend_dir, "replay.html"))

    @app.get("/routine")
    def serve_routine():
        return FileResponse(os.path.join(frontend_dir, "routine.html"))

    @app.get("/privacy")
    def serve_privacy():
        return FileResponse(os.path.join(frontend_dir, "privacy.html"))

    @app.get("/caregiver")
    def serve_caregiver():
        return FileResponse(os.path.join(frontend_dir, "caregiver.html"))

    @app.get("/camera")
    def serve_camera():
        return FileResponse(os.path.join(frontend_dir, "camera.html"))

    # Mount remaining static assets (CSS, JS, images)
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "system": "MemoryBridge AI",
        "version": "1.0.0",
        "philosophy": "The environment remembers, so they don't have to."
    }
