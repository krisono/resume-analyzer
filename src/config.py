from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str | None = None
    FLASK_ENV: str = "development"
    PORT: int = 5000
    model_config = {"env_file": ".env", "extra": "ignore"}