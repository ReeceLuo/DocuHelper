from pydantic_settings import BaseSettings

# App settings
class Settings(BaseSettings):
    DATABASE_URL: str
    model_config = {"env_file": ".env"}

# Load settings
settings = Settings()