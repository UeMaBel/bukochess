from fastapi import FastAPI
from .core.config import settings
from .api.v1.health import router as health_router


def create_application() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug)

    # Routers
    app.include_router(health_router, prefix=settings.api_v1_prefix)

    return app


app = create_application()
