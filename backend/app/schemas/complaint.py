from datetime import datetime
from typing import Optional
from services.complaint_service import get_complaints, get_complaint_by_key, get_cluster_stats
from pydantic import BaseModel, ConfigDict


class ComplaintOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    unique_key: int
    created_date: datetime
    closed_date: Optional[datetime] = None
    complaint_type: str
    descriptor: Optional[str] = None
    status: str
    borough: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    incident_zip: Optional[str] = None
    street_name: Optional[str] = None
    agency: str
    agency_name: Optional[str] = None


class ComplaintListResponse(BaseModel):
    items: list[ComplaintOut]
    next_cursor: Optional[str] = None