from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import get_settings
from contextlib import asynccontextmanager
from app.api.router import router
from app.core.logging import config_logging
from app.db.database import engine
from app.exceptions.auth_exception import EmailAlreadyRegisteredException, InvalidCredentialsException
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

@app.exception_handler(EmailAlreadyRegisteredException)
async def email_registered_handler(request: Request, exc: EmailAlreadyRegisteredException):
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": "Email is already registered"})

@app.exception_handler(InvalidCredentialsException)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsException):
    # Same message for unknown email and wrong password, so attackers can't probe emails
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Incorrect email or password"},
        headers={"WWW-Authenticate": "Bearer"},
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
        "details": "Auth Service is running"
    }
