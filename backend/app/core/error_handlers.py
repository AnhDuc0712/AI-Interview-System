import logging
import traceback

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    ProcessingError,
    ValidationError,
)

logger = logging.getLogger(__name__)


def _log_exception(request: Request, exc: Exception) -> None:
    logger.error(
        'Request failed: %s %s exception=%s\n%s',
        request.method,
        request.url.path,
        exc,
        ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AuthenticationError)
    async def handle_authentication_error(
        request: Request,
        exc: AuthenticationError
    ) -> JSONResponse:
        _log_exception(request, exc)
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={'detail': exc.detail}
        )

    @app.exception_handler(AuthorizationError)
    async def handle_authorization_error(
        request: Request,
        exc: AuthorizationError
    ) -> JSONResponse:
        _log_exception(request, exc)
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={'detail': exc.detail}
        )

    @app.exception_handler(ConfigurationError)
    async def handle_configuration_error(
        request: Request,
        exc: ConfigurationError
    ) -> JSONResponse:
        _log_exception(request, exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'detail': exc.detail}
        )

    @app.exception_handler(ValidationError)
    async def handle_validation_error(
        request: Request,
        exc: ValidationError
    ) -> JSONResponse:
        _log_exception(request, exc)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={'detail': exc.detail}
        )

    @app.exception_handler(ProcessingError)
    async def handle_processing_error(
        request: Request,
        exc: ProcessingError
    ) -> JSONResponse:
        _log_exception(request, exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'detail': exc.detail}
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        _log_exception(request, exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'detail': 'Internal server error'}
        )
