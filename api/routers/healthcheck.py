from starlette.responses import JSONResponse
import database
import settings
from fastapi import APIRouter
from models import HealthcheckModel, Message, ServiceHealthModel
import os
import signal

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
