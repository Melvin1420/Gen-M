from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Gen-M"
    app_env: str = "development"
    app_debug: bool = True

    api_v1_prefix: str = "/api/v1"

    mysql_host: str = "mysql"
    mysql_port: int = 3306
    mysql_database: str = "gen_m"
    mysql_user: str = "gen_m_user"
    mysql_password: str = "change_this_password"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:"
            f"{self.mysql_password}@"
            f"{self.mysql_host}:"
            f"{self.mysql_port}/"
            f"{self.mysql_database}"
        )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
