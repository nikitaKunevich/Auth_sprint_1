from pydantic import BaseSettings


class Settings(BaseSettings):
    LOG_LEVEL: str = "WARNING"
    REDIS_SOCKET: str = "127.0.0.1:6379"
    POSTGRES_URI: str = "postgresql://postgres@127.0.0.1:5432/auth"
    DEBUG: bool = False
    SECRET_KEY: str
    SECURITY_PASSWORD_SALT: str
    JSONIFY_PRETTYPRINT_REGULAR: bool = True


config = Settings()
