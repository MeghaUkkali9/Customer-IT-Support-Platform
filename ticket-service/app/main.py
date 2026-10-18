from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import get_settings
from contextlib import asynccontextmanager
from app.api.router import router
from app.core.logging import config_logging
from app.db.datbase import engine
from app.exceptions.ticket_exception import IdempotencyKeyReusedException, TicketNotFoundException
import logging

settings = get_settings()
config_logging(settings.log_level)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def life_span(app: FastAPI):
    logger.info("Service has started")
    
    yield
    logger.info("Service is shutting down")
    await engine.dispose()

app = FastAPI(title=settings.app_name, lifespan=life_span)

app.include_router(router=router)

@app.exception_handler(TicketNotFoundException)
async def ticket_not_found_handler(request: Request, exc: TicketNotFoundException):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": f"Ticket {exc} not found"})

@app.exception_handler(IdempotencyKeyReusedException)
async def idempotency_key_reused_handler(request: Request, exc: IdempotencyKeyReusedException):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": "Idempotency-Key was already used with a different request body"},
    )

@app.get("/")
async def check_health():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        logger.exception("Database health check failed")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "details": "Database is unreachable"},
        )
    return {
        "status": "ok",
        "details": "Ticket Service is running"
    }
    