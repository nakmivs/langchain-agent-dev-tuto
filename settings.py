from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    volcengine_api_key: str
    volcengine_api_base: str
    dashscope_api_key: str
    dashscope_api_base: str

settings = Settings()