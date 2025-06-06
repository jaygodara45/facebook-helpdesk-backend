from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import engine, Base, test_db_connection
from app.api.routes import auth
from app.api import facebook, messenger
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Facebook Helpdesk API...")
    
    # Test database connection
    if not test_db_connection():
        logger.error("Failed to connect to PostgreSQL database!")
        raise Exception("Database connection failed")
    
    logger.info("Database connection successful")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Facebook Helpdesk API...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
app.include_router(facebook.router)
app.include_router(messenger.router, prefix="/api/messenger", tags=["messenger"])

@app.get("/")
def read_root():
    return {
        "message": "Facebook Helpdesk API",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "database": "PostgreSQL"
    }

@app.get("/health")
def health_check():
    db_status = "healthy" if test_db_connection() else "unhealthy"
    
    if db_status == "unhealthy":
        raise HTTPException(status_code=503, detail="Database connection failed")
    
    return {
        "status": "healthy",
        "database": db_status,
        "version": settings.VERSION
    }