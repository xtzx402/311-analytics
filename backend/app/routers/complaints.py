from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.complaint import ComplaintOut, ComplaintListResponse
from services.complaint_service import get_complaints

router = APIRouter(prefix="/complaints", tags=["complaints"])


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