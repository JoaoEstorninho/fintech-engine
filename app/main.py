from fastapi import FastAPI
from app.api.routes import router
from app.core.logging_config import setup_logging
from app.core.db import Base, engine
from app.core.exceptions import AppException, app_exception_handler

app.add_exception_handler(AppException, app_exception_handler)
Base.metadata.create_all(bind=engine)

setup_logging()
app = FastAPI()
app.include_router(router)
