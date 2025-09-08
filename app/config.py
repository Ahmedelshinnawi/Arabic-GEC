from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str

    debug: bool = False
    port: int = 8000
    host: str = "0.0.0.0"

    model_name: str = "alnnahwi/gemma-3-1b-arabic-gec-v1"
    max_text_length: int = 5000

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
