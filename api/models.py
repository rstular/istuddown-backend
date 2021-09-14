from enum import IntEnum
from typing import List

from pydantic import AnyHttpUrl, BaseModel, Field


class ServiceStatus(IntEnum):
    ONLINE = 0
    DEGRADED = 1
    OFFLINE = 2
    UNKNOWN = 3


class ServiceModel(BaseModel):
    name: str = Field(...)
    display_name: str = Field(...)
    display_url: AnyHttpUrl = Field(...)
    description: str = Field(...)


class ServiceDetailedModel(ServiceModel):
    active: int = Field(...)
    check_url: AnyHttpUrl = Field(...)


class ServiceHealthModel(ServiceModel):

    ping: float = Field(...)
    status: ServiceStatus = Field(...)

    class Config:
        allow_population_by_field_name = True


class HealthcheckModel(BaseModel):

    timestamp: int = Field(...)
    services: List[ServiceHealthModel] = Field(...)

    class Config:
        allow_population_by_field_name = True


class Message(BaseModel):
    message: str
