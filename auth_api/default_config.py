class DefaultConfig:
    JWT_ACCESS_LIFESPAN = {"minutes": 15}
    JWT_REFRESH_LIFESPAN = {"days": 30}
    PRAETORIAN_HASH_SCHEME = "argon2"
    JWT_PLACES = ["header"]
