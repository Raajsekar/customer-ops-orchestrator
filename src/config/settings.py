from functools import lru_cache
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load .env once at startup
load_dotenv()


class Settings(BaseModel):
    env: str = os.getenv("APP_ENV", "local")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    dynamodb_table: str = os.getenv("DDB_TICKET_TABLE", "tickets-dev")

    langfuse_public_key: str | None = os.getenv("LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str | None = os.getenv("LANGFUSE_SECRET_KEY")
    # support both LANGFUSE_BASE_URL and LANGFUSE_HOST
    langfuse_host: str | None = os.getenv("LANGFUSE_BASE_URL") or os.getenv("LANGFUSE_HOST")

    

@lru_cache
def get_settings() -> Settings:
    return Settings()
