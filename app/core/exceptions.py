from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


# 🔹 Specific exceptions

class ValidationException(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class NotFoundException(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class ConflictException(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=409)


class ExternalServiceException(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=502)


# 🔹 Global handler

async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message
        }
    )