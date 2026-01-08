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
    print("\n" + "="*80)
    print("🤖 Initializing Jarvis Backend...")
    print("="*80)
    try:
        print("[STARTUP] Creating JarvisOrchestrator instance...")
        orchestrator = JarvisOrchestrator()

        print("[STARTUP] Calling orchestrator.initialize()...")
        await orchestrator.initialize()

        print("="*80)
        print("✅ Jarvis Backend is ready!")
        print("="*80 + "\n")
    except Exception as e:
        print("="*80)
        print(f"⚠️ Warning during Jarvis initialization: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        print("="*80)
        print("[STARTUP] Attempting to create minimal orchestrator instance...")
        # Ensure orchestrator is still created even if initialization partially failed
        try:
            orchestrator = JarvisOrchestrator()
            print("[STARTUP] Minimal orchestrator created. Backend will use fallback NLP")
        except Exception as fallback_error:
            print(f"[STARTUP] ERROR: Could not even create minimal orchestrator: {fallback_error}")
            orchestrator = None

    yield

    print("\n👋 Shutting down Jarvis...")
    try:
        if orchestrator:
            await orchestrator.cleanup()
            print("✅ Jarvis shutdown complete")
    except Exception as e:
        print(f"⚠️ Error during cleanup: {e}")


# Create FastAPI app
app = FastAPI(
    title="Jarvis 3D AI",
    description="A Jarvis-like AI for interactive 3D content generation",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware - allow all origins for Railway deployment
# In production, check if we're running on Railway
is_production = os.getenv("RAILWAY_ENVIRONMENT_NAME") or os.getenv("PORT")

if is_production:
    # Railway deployment - allow all origins
    allow_origins = ["*"]
else:
    # Local development
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True if not is_production else False,
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
    openai_key_set = bool(os.getenv("OPENAI_API_KEY"))

    health_status = {
        "status": "healthy" if orchestrator is not None else "unhealthy",
        "orchestrator_ready": orchestrator is not None,
        "openai_api_key_set": openai_key_set,
    }

    if orchestrator:
        health_status["modules"] = {
            "nlp": orchestrator.nlp_processor is not None,
            "cv": orchestrator.cv_processor is not None,
            "text_to_3d": orchestrator.text_to_3d is not None,
            "scene_builder": orchestrator.scene_builder is not None
        }
        # Check if OpenAI client is initialized
        if orchestrator.nlp_processor:
            health_status["openai_client_initialized"] = orchestrator.nlp_processor.client is not None

    return health_status


@app.get("/api/health")
async def api_health_check():
    """API Health check endpoint"""
    openai_key_set = bool(os.getenv("OPENAI_API_KEY"))

    health_status = {
        "status": "healthy" if orchestrator is not None else "unhealthy",
        "orchestrator_ready": orchestrator is not None,
        "openai_api_key_set": openai_key_set,
    }

    if orchestrator:
        health_status["modules"] = {
            "nlp": orchestrator.nlp_processor is not None,
            "cv": orchestrator.cv_processor is not None,
            "text_to_3d": orchestrator.text_to_3d is not None,
            "scene_builder": orchestrator.scene_builder is not None
        }
        # Check if OpenAI client is initialized
        if orchestrator.nlp_processor:
            health_status["openai_client_initialized"] = orchestrator.nlp_processor.client is not None

    return health_status


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
