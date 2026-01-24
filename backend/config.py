from pydantic_settings import BaseSettings

# App settings
class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SIGNING_KEY: str
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: list = ["pdf", "docx", "txt"]
    model_config = {"env_file": ".env"}

# Load settings
settings = Settings()