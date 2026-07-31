from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from services.complaint_service import get_complaints, get_complaint_by_key, get_cluster_stats, get_distinct_complaint_types
from database import get_db
from schemas.complaint import ComplaintOut, ComplaintListResponse
from services.complaint_service import get_complaints

from fastapi import HTTPException

from services.complaint_service import get_complaints, get_complaint_by_key

router = APIRouter(prefix="/complaints", tags=["complaints"])

def zoom_to_grid_size(zoom: int) -> float:
    return max(0.001, 0.5 / (2 ** (zoom - 8)))

@router.get("", response_model=ComplaintListResponse)
def list_complaints(
    limit: int = Query(50, ge=1, le=500),
    cursor: Optional[str] = None,
    borough: Optional[str] = None,
    complaint_type: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    rows, next_cursor = get_complaints(
        db=db,
        limit=limit,
        cursor=cursor,
        borough=borough,
        complaint_type=complaint_type,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )
    return ComplaintListResponse(
        items=[ComplaintOut.model_validate(r) for r in rows],
        next_cursor=next_cursor,
    )

@router.get("/clusters")
def get_clusters(
    min_lat: float,
    max_lat: float,
    min_lon: float,
    max_lon: float,
    zoom: int = Query(11, ge=1, le=20),
    db: Session = Depends(get_db),
):
    grid_size = zoom_to_grid_size(zoom)
    clusters = get_cluster_stats(
        db=db,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
        grid_size=grid_size,
    )
    return {"grid_size": grid_size, "clusters": clusters}

@router.get("/types")
def list_complaint_types(db: Session = Depends(get_db)):
    return {"types": get_distinct_complaint_types(db)}

@router.get("/{unique_key}", response_model=ComplaintOut)
def get_complaint(unique_key: int, db: Session = Depends(get_db)):
    complaint = get_complaint_by_key(db, unique_key)
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return ComplaintOut.model_validate(complaint)