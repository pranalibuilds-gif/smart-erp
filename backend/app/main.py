from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import logger
from app.core.exceptions import setup_exception_handlers
from app.api.v1.router import api_v1_router

@asynccontextmanager
async def lifespan(application: FastAPI):
    # Startup logic
    logger.info("Application starting up...")
    yield
    # Shutdown logic
    logger.info("Application shutting down...")

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.APP_DEBUG,
        version="0.1.0",
        lifespan=lifespan
    )

    # Set up CORS
    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Set up exception handlers
    setup_exception_handlers(application)

    # Include routers
    application.include_router(api_v1_router, prefix=settings.API_V1_STR)

    return application

app = create_application()
