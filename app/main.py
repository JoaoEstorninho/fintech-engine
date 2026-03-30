from fastapi import FastAPI
from app.api.routes import router
from app.core.logging_config import setup_logging
from app.core.db import Base, engine
from app.core.exceptions import AppException, app_exception_handler

# Setup logging first
setup_logging()

# Create app
app = FastAPI()

# Register exception handler
app.add_exception_handler(AppException, app_exception_handler)

# Register routes
app.include_router(router)


# ✅ Better: run DB init on startup
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)