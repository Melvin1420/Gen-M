from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Gen-M"
    app_env: str = "development"
    app_debug: bool = True

    secret_key: str
    access_token_expire_minutes: int = 30

    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_database: str = "gen_m"
    mysql_user: str
    mysql_password: str

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()