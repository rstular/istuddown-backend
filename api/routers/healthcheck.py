import os
import signal

import database
import settings
from fastapi import APIRouter
from models import (
    HealthcheckModel,
    HealthcheckTinyModel,
    Message,
    ServiceHealthModel,
    ServiceStatus,
)
from starlette.responses import JSONResponse

router = APIRouter(prefix="/healthcheck", tags=["healthcheck"], redirect_slashes=False)


@router.get(
    "/latest/",
    name="latest",
    summary="Get results of the latest healthcheck",
    response_description="Latest healthcheck result of all services",
    response_model=HealthcheckModel,
)
async def get_latest_healthcheck():

    latest_healthcheck = (
        await database.get_db()[settings.HEALTHCHECK_COLLECTION]
        .find({}, {"_id": False})
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
            {"_id": service["service_id"]},
            {"_id": False, "active": False, "check_url": False},
        )

        service_obj = ServiceHealthModel(
            **service_info, ping=service["ping"], status=service["status"]
        )
        response_object["services"].append(service_obj)

    return response_object


@router.get(
    "/tiny/",
    name="tiny",
    summary="Return the status of the worst-performing service",
    response_description="Status number of the worst-performing service",
    response_model=HealthcheckTinyModel,
)
async def get_tiny_healthcheck():
    latest_healthcheck = (
        await database.get_db()[settings.HEALTHCHECK_COLLECTION]
        .find({}, {"_id": False})
        .sort([("timestamp", -1)])
        .limit(1)
        .next()
    )

    response_object: HealthcheckTinyModel = {
        "timestamp": latest_healthcheck["timestamp"]
    }

    worstStatus = ServiceStatus.ONLINE
    for service in latest_healthcheck["services"]:
        if service["status"] < 3 and service["status"] > worstStatus:
            worstStatus = service["status"]

            if worstStatus == ServiceStatus.OFFLINE:
                break

    response_object["status"] = worstStatus
    return response_object


@router.post(
    "/",
    name="perform",
    summary="Request another healthcheck",
    response_model=Message,
    response_description="Whether the request for another healthcheck was sent",
    responses={503: {"model": Message}},
)
async def perform_healthcheck():
    try:
        with open(settings.DAEMON_PIDFILE) as f:
            pid = int(f.read())
        os.kill(pid, signal.SIGUSR1)
    except:
        return JSONResponse(
            status_code=503, content={"message": "Daemon is unavailable at the moment"}
        )

    return JSONResponse(
        content={"message": "Request for another healthcheck was sent."}
    )


@router.get(
    "/latest/{name}",
    name="latest_service",
    summary="Get latest healthcheck result for a specific service",
    response_model=ServiceHealthModel,
    response_description="Latest healthcheck result for the specified service",
    responses={404: {"model": Message}},
)
async def get_latest_service(name):

    service_info = await database.get_db()[settings.SERVICES_COLLECTION].find_one(
        {"name": name}, {"active": False, "check_url": False}
    )
    if service_info is None:
        return JSONResponse(status_code=404, content={"message": "Service not found"})

    latest_healthcheck = (
        await database.get_db()[settings.HEALTHCHECK_COLLECTION]
        .find({}, {"_id": False})
        .sort([("timestamp", -1)])
        .limit(1)
        .next()
    )
    for service in latest_healthcheck["services"]:
        if service["service_id"] == service_info["_id"]:
            return ServiceHealthModel(
                ping=service["ping"], status=service["status"], **service_info
            )

    return JSONResponse(
        status_code=404,
        content={
            "message": "Healthcheck result not found - the service may be inactive"
        },
    )
