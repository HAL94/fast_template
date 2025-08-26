
from pydantic_settings import BaseSettings, SettingsConfigDict

class OAuthSettings(BaseSettings):
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_SERVER_URL: str
    KEYCLOAK_REALM: str
    KEYCLOAK_TOKEN_URL: str
    KEYCLOAK_REDIRECT_URI: str
    KEYCLOAK_METADATA_URI: str

class AppConfigSettings(BaseSettings):
    ENV: str = "prod"
    APP_PORT: int = 8000
    HOST: str = "localhost"
    ALLOWED_ORIGIN: str
    SESSION_SECRET: str


class PostgresSettings(BaseSettings):
    PG_USER: str
    PG_PW: str
    PG_SERVER: str
    PG_PORT: str
    PG_DB: str


class Settings(PostgresSettings, OAuthSettings, AppConfigSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8')


settings = Settings()


def get_settings() -> Settings:
    global settings
    if settings is None:
        settings = Settings()
    return settings
