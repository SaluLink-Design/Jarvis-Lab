"""
Jarvis Backend - Main Application Entry Point
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]

from core.orchestrator import JarvisOrchestrator
from api.routes import router

# Load environment variables
load_dotenv()

# Initialize orchestrator
orchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global orchestrator
    print("🤖 Initializing Jarvis...")
    try:
        orchestrator = JarvisOrchestrator()
        await orchestrator.initialize()
        print("✅ Jarvis is ready!")
    except Exception as e:
        print(f"❌ Error initializing Jarvis: {e}")
        import traceback
        traceback.print_exc()
        orchestrator = None

    yield

    print("👋 Shutting down Jarvis...")
    try:
        if orchestrator:
            await orchestrator.cleanup()
    except Exception as e:
        print(f"⚠️ Error during cleanup: {e}")


# Create FastAPI app
app = FastAPI(
    title="Jarvis 3D AI",
    description="A Jarvis-like AI for interactive 3D content generation",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware - allow all origins in development, be more restrictive in production
allow_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173"
]

# Add deployed frontend origins if specified
deployed_frontend = os.getenv("FRONTEND_URL")
if deployed_frontend:
    allow_origins.append(deployed_frontend)

# In production, also allow the fly.dev domain pattern
if not os.getenv("DEBUG", "True").lower() == "true":
    allow_origins.append("*")  # More permissive in production, can be restricted later

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
os.makedirs("uploads", exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include API routes
app.include_router(router, prefix="/api")

# Include simulation routes
from api.simulation_routes import router as simulation_router
app.include_router(simulation_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Jarvis 3D AI",
        "version": "0.1.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "orchestrator_ready": orchestrator is not None
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )
