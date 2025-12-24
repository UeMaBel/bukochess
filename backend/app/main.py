from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.health import router as health_router
from app.core.logger import get_logger

from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException

from app.core.exception_handler import (
    bukochess_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)
from app.core.exceptions import BukochessException
from app.api.v1.position import router as position_router
from app.api.v1.game import router as game_router
from app.api.v1.engine import router as engine_router

logger = get_logger(__name__)


def create_application() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    logger.info("Starting Bukochess backend...")

    # Routers
    app.include_router(health_router, prefix=settings.api_v1_prefix)
    app.include_router(position_router, prefix=settings.api_v1_prefix + "/position")
    app.include_router(game_router, prefix=settings.api_v1_prefix + "/game")
    app.include_router(engine_router, prefix=settings.api_v1_prefix + "/engine")

    # exception handlers
    app.add_exception_handler(BukochessException, bukochess_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    for route in app.routes:
        print(route.path, route.name)

    return app


app = create_application()
