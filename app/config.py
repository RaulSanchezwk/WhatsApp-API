import os
from dotenv import load_dotenv

env = os.getenv("ENV", "development")

if env == "production":
    load_dotenv(".env.production")
else:
    load_dotenv(".env")

class Settings:
    VERIFY_TOKEN: str = os.getenv("VERIFY_TOKEN")
    ACCESS_TOKEN: str = os.getenv("WHATSAPP_ACCESS_TOKEN")
    PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    DEBUG: bool = env == "development"

settings = Settings()
