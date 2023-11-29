from pydantic import AnyUrl, SecretStr
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class AppSettings(BaseSettings):
    project_name: str = "Поиск работы"
    log_lvl: str = 'DEBUG'


class UserDBSettings(BaseSettings):
    name: str
    user: str
    password: SecretStr
    port: int
    host: str

    class Config:
        env_prefix = "db_"

    def _url(cls) -> AnyUrl:
        return f"postgresql+asyncpg://{cls.user}:{cls.password.get_secret_value()}"\
               f"@{cls.host}:{cls.port}/{cls.name}"

    @property
    def async_url(cls) -> AnyUrl:
        return cls._url()


class TokenSettings(BaseSettings):
    access_expire: int = 10
    access_secret_key: SecretStr
    refresh_expire: int = 60
    refresh_secret_key: SecretStr
    refresh_token_cookie_name: str = "refresh_token"
    algorithm: str = "HS256"

    class Config:
        env_prefix = "token_"


class RedisSettings(BaseSettings):
    host: str = "redis_token"
    port: int = 6379
    password: SecretStr

    class Config:
        env_prefix = "redis_"


class JWTSetting(BaseSettings):
    REQUEST_LIMIT_PER_MINUTE: int = 20


app_settings = AppSettings()
token_settings = TokenSettings()
redis_settings = RedisSettings()
db_settings = UserDBSettings()
