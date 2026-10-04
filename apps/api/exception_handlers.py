import logging

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

async def invalid_file_exception_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.warning("Invalid file request: %s", exc)

    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )