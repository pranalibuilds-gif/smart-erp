import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.shared.schemas.responses import ErrorResponse

logger = logging.getLogger(__name__)

def setup_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                message=str(exc.detail),
                success=False
            ).model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        from fastapi.encoders import jsonable_encoder
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                message="Validation error",
                data=jsonable_encoder(exc.errors()),
                success=False
            ).model_dump()
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # Log the actual exception
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal server error",
                "success": False
            }
        )
