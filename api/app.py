from enum import IntEnum
from typing import List

import motor.motor_asyncio
import uvicorn
from bson import ObjectId
from fastapi import FastAPI
from pydantic import AnyHttpUrl, BaseModel, Field

import settings
import database

app = FastAPI(
    redoc_url=None,
    title="Is TU Delft down? API",
    root_path="/api/v1"
)
# Disable redirection of slashes
app.router.redirect_slashes = False

# Connect to database on startup
app.add_event_handler("startup", database.connect_db)
# Disconnect from database on shutdown
app.add_event_handler("shutdown", database.close_db)

class ServiceStatus(IntEnum):
    ONLINE = 0
    DEGRADED = 1
    OFFLINE = 2
    UNKNOWN = 3

class ServiceHealthModel(BaseModel):

    name: str = Field(...)
    display_name: str = Field(...)
    display_url: AnyHttpUrl = Field(...)
    description: str = Field(...)
    check_url: AnyHttpUrl = Field(...)
    ping: float = Field(...)
    status: ServiceStatus = Field(...)

    class Config:
        allow_population_by_field_name = True


class HealthcheckModel(BaseModel):

    timestamp: int = Field(...)
    services: List[ServiceHealthModel] = Field(...)

    class Config:
        allow_population_by_field_name = True


@app.get(
    "/latest/",
    response_description="Latest healthcheck result of all services",
    response_model=HealthcheckModel,
)
async def get_latest_healthcheck():

    latest_healthcheck = (
        await database.get_db()[settings.HEALTHCHECK_COLLECTION]
        .find()
        .sort([("timestamp", -1)])
        .limit(1)
        .next()
    )

    response_object: HealthcheckModel = {
        "timestamp": latest_healthcheck["timestamp"],
        "services": [],
    }

    for service in latest_healthcheck["services"]:

        service_info = await database.get_db()[settings.SERVICES_COLLECTION].find_one(
            {"_id": service["service_id"]}
        )

        service_obj: ServiceHealthModel = {
            "name": service_info["name"],
            "display_name": service_info["display_name"],
            "display_url": service_info["display_url"],
            "description": service_info["description"],
            "check_url": service_info["check_url"],
            "ping": service["ping"],
            "status": service["status"],
        }

        response_object["services"].append(service_obj)

    return response_object

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

