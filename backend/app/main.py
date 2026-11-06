"""
AI Calling Agent — FastAPI Application Entry Point

Registers all routers, configures CORS, and initializes the database on startup.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers import agents, conversation, providers, settings, tts

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup."""
    logger.info("🚀 Starting AI Calling Agent...")
    await init_db()
    logger.info("✅ Database initialized")

    app_settings = get_settings()
    logger.info("📡 Active LLM Provider: %s", app_settings.LLM_PROVIDER)
    if app_settings.LLM_FALLBACK_PROVIDER:
        logger.info("🔄 Fallback Provider: %s", app_settings.LLM_FALLBACK_PROVIDER)

    yield

    logger.info("👋 Shutting down AI Calling Agent")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Calling Agent",
    description="Provider-agnostic AI calling agent with Ollama and Gemini support",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(settings.router)
app.include_router(providers.router)
app.include_router(agents.router)
app.include_router(conversation.router)
app.include_router(tts.router)


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "name": "AI Calling Agent",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
