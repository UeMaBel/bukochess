from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.health import router as health_router
from app.core.logger import get_logger

logger = get_logger(__name__)


def create_application() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    logger.info("Starting Bukochess backend...")

    # Routers
    app.include_router(health_router, prefix=settings.api_v1_prefix)

    return app


app = create_application()
