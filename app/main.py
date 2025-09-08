from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import router as api_router
from app.config import get_settings
from app.services.correction_service import correction_service
from app.web.routes import router as web_router
from logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    try:
        correction_service.initialize_model()
        logger.info("Model initialization completed")
    except Exception as e:
        logger.error(f"Failed to initialize model: {e}")

    yield

    # Shutdown
    logger.info("Shutting down...")


settings = get_settings()

app = FastAPI(
    title="Arabic Text Correction API",
    description="Web application for correcting Arabic text using AI",
    version="2.0.0",
    lifespan=lifespan,
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(api_router)
app.include_router(web_router)
