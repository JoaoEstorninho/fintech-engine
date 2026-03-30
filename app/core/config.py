from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "prod"  # dev | test | prod

    DATABASE_URL: str = "sqlite:///./test.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_TASK_ALWAYS_EAGER: bool = False
    CELERY_TASK_IGNORE_RESULT: bool = False

    class Config:
        env_file = ".env"


settings = Settings()