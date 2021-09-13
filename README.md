# Is TU Delft down? Backend service

## API

Api requires a `.env` file to run properly. The file should have the following structure:

```bash
MONGO_USER="user"
MONGO_PASS="pass"
MONGO_DB="istudelftdown"
MONGO_HOST="localhost"
MONGO_PORT="27017"
HEALTHCHECK_COLLECTION="healthchecks"
SERVICE_COLLECTION="services"
```

## Service

The script `service/healthcheck.py` should be executed in regular intervals by a Cron job. The script optionally takes one argument, path to `config.json`. If argument is not provided, the directory of `config.json` is assumed to be `$PWD`.

Script also requires a `.env` file, with the following structure:

```bash
MONGO_USER="user"
MONGO_PASS="pass"
MONGO_DB="istudelftdown"
MONGO_HOST="localhost"
MONGO_PORT="27017"
```
