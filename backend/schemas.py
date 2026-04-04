from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.models import IncidentStatus


class IncidentBase(BaseModel):
    title: str
    description: str
    location: str


class IncidentCreate(IncidentBase):
    pass


class IncidentRead(IncidentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: IncidentStatus
    created_at: datetime
