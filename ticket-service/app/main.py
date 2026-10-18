from fastapi import FastAPI
from app.core.config import get_settings
from contextlib import asynccontextmanager
from app.api.router import router
from app.core.logging import config_logging
import logging

settings = get_settings()
config_logging(settings.log_level)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def life_span(app: FastAPI):
    logger.info("Service has started")
    
    yield
    logger.info("Service is shutting down")

app = FastAPI(title=settings.app_name, lifespan=life_span)

app.include_router(router=router)

@app.get("/")
async def check_health():
    return {
        "status": "ok",
        "details": "Ticket Service is running"
    }
    