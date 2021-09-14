import database
import settings
from fastapi import APIRouter
from models import HealthcheckModel, ServiceHealthModel

router = APIRouter(prefix="/healthcheck", tags=["healthcheck"], redirect_slashes=False)


@router.get(
    "/latest/",
    name="latest",
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
