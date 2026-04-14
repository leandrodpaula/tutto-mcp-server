from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Tutto MCP Server"
    MONGODB_URL: str
    MONGODB_DATABASE_NAME: str = "tuttoDb"
    MERCADO_PAGO_ACCESS_TOKEN: str = ""
    MERCADO_PAGO_BACK_URL_BASE: str = "https://tutto.example.com"
    PORT: int = Field(8000, alias="SERVER_PORT")
    MCP_TRANSPORT: str = Field("http", alias="MCP_TRANSPORT")
    LOG_LEVEL: str = "INFO"
    EVOLUTION_API_URL: str = "http://127.0.0.1:8080"
    EVOLUTION_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
