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
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str


    class Config:
        env_file = f".env.{env}"
        case_sensitive = True

settings = Settings()
