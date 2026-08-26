from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import db_manager
from app.auth.router import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect database
    db_manager.connect()
    yield
    # Disconnect database
    db_manager.disconnect()

app = FastAPI(
    title="Klink AI Video Core Platform",
    description="Fullstack Polyglot AI Video Platform Backend",
    version="1.0.0",
    lifespan=lifespan
)

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)

@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "healthy", "service": "klink-api-gateway"}
