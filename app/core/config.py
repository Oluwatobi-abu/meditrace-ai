from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GROQ_API_KEY: str
    APP_NAME: str = "MediTrace AI"
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()