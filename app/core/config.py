from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()