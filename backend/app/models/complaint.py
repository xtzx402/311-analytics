from datetime import datetime
from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    unique_key: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_date: Mapped[datetime] = mapped_column(DateTime, index=True)
    closed_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    complaint_type: Mapped[str] = mapped_column(String, index=True)
    descriptor: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, index=True)

    borough: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    city: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    incident_zip: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    street_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )

    agency: Mapped[str] = mapped_column(String, index=True)
    agency_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    def __repr__(self) -> str:
        return f"<Complaint(unique_key={self.unique_key}, type={self.complaint_type})>"