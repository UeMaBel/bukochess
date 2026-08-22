import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.logger import get_logger
from app.core.exceptions import BukochessException
from app.core.config import settings

logger = get_logger(__name__)


async def bukochess_exception_handler(request: Request, exc: BukochessException):
    logger.warning(f"Handled BukochessException: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception at {request.url}: {exc}\n"
        f"{traceback.format_exc()}"
    )

    # Hide implementation details in production
    if settings.debug:
        detail = str(exc)
    else:
        detail = "Internal server error"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail},
    )
