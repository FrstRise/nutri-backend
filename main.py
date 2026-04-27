from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import ping_db, close_db
from app.api.auth import router as auth_router
from app.api.onboarding import router as onboarding_router


# ---------------------------------------------------------------------------
# Lifespan — startup / shutdown hooks
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    print("🚀 NutriAI Backend starting...")
    connected = await ping_db()
    if connected:
        print("✅ MongoDB connected successfully.")
    else:
        print("❌ MongoDB connection FAILED — check MONGO_URI in .env")
    yield
    # SHUTDOWN
    await close_db()
    print("🛑 NutriAI Backend shut down.")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="NutriAI API",
    version="1.0.0",
    description="Backend for the NutriAI nutrition tracking platform.",
    lifespan=lifespan,
)

# CORS — allow the Vite dev server (port 5173) and production origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev
        "http://localhost:4173",  # Vite preview
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth_router,       prefix="/api")
app.include_router(onboarding_router, prefix="/api")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/api/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "NutriAI API"}
