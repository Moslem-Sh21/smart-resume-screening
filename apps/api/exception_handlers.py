from fastapi import Request
from fastapi.responses import JSONResponse


async def invalid_file_exception_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )