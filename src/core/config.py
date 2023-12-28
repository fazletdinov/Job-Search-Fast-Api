from pprint import pprint
from pathlib import Path

from pydantic import SecretStr, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent


class AppSettings(BaseModel):
    project_name: str = "Поиск работы"
    log_lvl: str = 'DEBUG'


class UserDBSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='db_',
                                      env_file=BASE_DIR / '.env',
                                      env_file_encoding='utf-8')

    name: str
    user: str
    password: SecretStr
    port: int
    host: str
    echo: bool = True
    future: bool = True

    def _url(self):
        return f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}" \
               f"@{self.host}:{self.port}/{self.name}"

    @property
    def async_url(self):
        return self._url()


class TokenSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='token_',
                                      env_file=BASE_DIR / ".env")

    access_expire: int = 10
    access_secret_key: SecretStr
    refresh_expire: int = 60
    refresh_secret_key: SecretStr
    refresh_token_cookie_name: str = "refresh_token"
    algorithm: str = "HS256"


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="redis_",
                                      env_file=BASE_DIR / ".env")

    host: str
    port: int
    password: SecretStr


class JWTSetting(BaseSettings):
    REQUEST_LIMIT_PER_MINUTE: int = 20


class Settings:
    app: AppSettings = AppSettings()
    token: TokenSettings = TokenSettings()
    redis: RedisSettings = RedisSettings()
    db: UserDBSettings = UserDBSettings()


settings = Settings()

if __name__ == "__main__":
    settings = Settings()
    pprint(settings.db.async_url)
