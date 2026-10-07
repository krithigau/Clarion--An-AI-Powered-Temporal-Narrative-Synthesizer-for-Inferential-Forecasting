import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📡 API Host: {settings.API_HOST}:{settings.API_PORT}")
    print(f"🧠 Cognitive Model: {settings.GEMINI_MODEL}")
    yield
    # Shutdown actions
    print(f"🛑 Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="An AI-Powered Temporal Narrative Synthesizer for Inferential Forecasting",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "platform": settings.APP_NAME,
        "tagline": "Beyond the Headline — An AI-Powered Temporal Narrative Synthesizer for Inferential Forecasting",
        "version": settings.APP_VERSION,
        "documentation": "/docs",
        "endpoints": {
            "health": "/api/health",
            "benchmark_topics": "/api/benchmark-topics",
            "harvest_discourse": "POST /api/harvester/harvest"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
