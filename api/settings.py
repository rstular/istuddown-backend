from starlette.config import Config

config = Config(".env")

MONGO_USER = config("MONGO_USER", cast=str, default="admin")
MONGO_PASS = config("MONGO_PASS", cast=str, default="admin")
MONGO_DB = config("MONGO_DB", cast=str, default="istudelftdown")
MONGO_HOST = config("MONGO_HOST", cast=str, default="localhost")
MONGO_PORT = config("MONGO_PORT", cast=int, default=27017)

MONGO_URL = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"

HEALTHCHECK_COLLECTION = config(
    "HEALTHCHECK_COLLECTION", cast=str, default="healthchecks"
)
SERVICES_COLLECTION = config("SERVICE_COLLECTION", cast=str, default="services")

IS_DEBUG = config("HCDEBUG", cast=int, default=0)
