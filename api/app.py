from enum import IntEnum
from typing import List

import uvicorn
from fastapi import FastAPI

import database
import settings
from routers import healthcheck, services

if settings.IS_DEBUG:
    app = FastAPI(title="Is TU Delft down? API")
else:
    app = FastAPI(redoc_url=None, title="Is TU Delft down? API", root_path="/api/v1")

# Disable redirection of slashes
app.router.redirect_slashes = False

# Connect to database on startup
app.add_event_handler("startup", database.connect_db)
# Disconnect from database on shutdown
app.add_event_handler("shutdown", database.close_db)

app.include_router(healthcheck.router)
app.include_router(services.router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
