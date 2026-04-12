from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
    )

    """Database settings"""

    postgres_database_name: str
    postgres_host: str
    postgres_port: int
    postgres_username: str
    postgres_password: str

    @property
    def postgres_connection_url_async(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_username}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_database_name}"
        )

    @property
    def postgres_connection_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_username}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_database_name}"
        )

    """Events provider settings"""

    events_provider_base_url: str
    events_provider_api_key: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
