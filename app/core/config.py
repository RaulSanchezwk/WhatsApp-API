from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Carga dinámica del entorno
env = os.getenv("ENV", "development")
load_dotenv(f".env.{env}")

class Settings(BaseSettings):
    VERIFY_TOKEN: str
    ACCESS_TOKEN: str
    PHONE_NUMBER_ID: str
    DEBUG: bool = env == "development"
    ENV: str

    CITAS_DB_HOST: str
    CITAS_DB_PORT: int
    CITAS_DB_USER: str
    CITAS_DB_PASSWORD: str
    CITAS_DB_NAME: str
    
    WEBHOOK_DB_HOST: str
    WEBHOOK_DB_PORT: int
    WEBHOOK_DB_USER: str
    WEBHOOK_DB_PASSWORD: str
    WEBHOOK_DB_NAME: str


    class Config:
        env_file = f".env.{env}"
        case_sensitive = True

settings = Settings()
