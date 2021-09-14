from enum import IntEnum
from typing import List

from pydantic import AnyHttpUrl, BaseModel, Field


class ServiceStatus(IntEnum):
    ONLINE = 0
    DEGRADED = 1
    OFFLINE = 2
    UNKNOWN = 3


class HealthcheckTinyModel(BaseModel):
    timestamp: int = Field(...)
    status: ServiceStatus = Field(...)


class ServiceShortModel(BaseModel):
    name: str = Field(...)
    display_name: str = Field(...)
    display_url: AnyHttpUrl = Field(...)


class ServiceModel(ServiceShortModel):
    description: str = Field(...)


class ServiceDetailedModel(ServiceModel):
    active: int = Field(...)
    check_url: AnyHttpUrl = Field(...)


class ServiceShortHealthModel(ServiceShortModel):
    ping: float = Field(...)
    status: ServiceStatus = Field(...)


class ServiceHealthModel(ServiceModel):
    ping: float = Field(...)
    status: ServiceStatus = Field(...)


class HealthcheckShortModel(BaseModel):
    timestamp: int = Field(...)
    services: List[ServiceShortHealthModel] = Field(...)


class ServiceHealthTimestampModel(ServiceHealthModel):
    timestamp: int = Field(...)


class HealthcheckModel(BaseModel):
    timestamp: int = Field(...)
    services: List[ServiceHealthModel] = Field(...)


class Message(BaseModel):
    message: str
