from typing import List

import database
import settings
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models import Message, ServiceDetailedModel

router = APIRouter(prefix="/services", tags=["services"], redirect_slashes=False)


@router.get(
    "/active/",
    summary="Get the list of actively tracked services",
    response_model=List[ServiceDetailedModel],
    response_description="List of actively tracked services",
)
async def get_active_services():

    # XXX: Fetch max 1000 results
    active_services = (
        await database.get_db()[settings.SERVICES_COLLECTION]
        .find({"active": 1}, {"_id": False})
        .to_list(1000)
    )

    response_object = []
    for service in active_services:
        response_object.append(service)

    return response_object


@router.get(
    "/{name}",
    summary="Get information about tracked service with given name",
    response_model=ServiceDetailedModel,
    response_description="information about tracked service with given name",
    responses={404: {"model": Message}},
)
async def get_service_info(name: str):
    service_info = await database.get_db()[settings.SERVICES_COLLECTION].find_one(
        {"name": name}, {"_id": False}
    )
    if service_info is None:
        return JSONResponse(status_code=404, content={"message": "Service not found"})

    response_obj = ServiceDetailedModel(**service_info)
    return response_obj
