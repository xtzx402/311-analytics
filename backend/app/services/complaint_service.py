import base64
import json
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Complaint


def encode_cursor(created_date: datetime, unique_key: int) -> str:
    raw = json.dumps({"created_date": created_date.isoformat(), "unique_key": unique_key})
    return base64.urlsafe_b64encode(raw.encode()).decode()


def decode_cursor(cursor: str) -> tuple[datetime, int]:
    raw = base64.urlsafe_b64decode(cursor.encode()).decode()
    data = json.loads(raw)
    return datetime.fromisoformat(data["created_date"]), data["unique_key"]

def get_complaint_by_key(db: Session, unique_key: int) -> Complaint | None:
    stmt = select(Complaint).where(Complaint.unique_key == unique_key)
    return db.execute(stmt).scalar_one_or_none()

def get_complaints(
    db: Session,
    limit: int = 50,
    cursor: Optional[str] = None,
    borough: Optional[str] = None,
    complaint_type: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    stmt = select(Complaint).order_by(Complaint.created_date, Complaint.unique_key)

    if borough:
        stmt = stmt.where(Complaint.borough == borough)
    if complaint_type:
        stmt = stmt.where(Complaint.complaint_type == complaint_type)
    if status:
        stmt = stmt.where(Complaint.status == status)
    if start_date:
        stmt = stmt.where(Complaint.created_date >= start_date)
    if end_date:
        stmt = stmt.where(Complaint.created_date <= end_date)

    if cursor:
        cursor_date, cursor_key = decode_cursor(cursor)
        stmt = stmt.where(
            (Complaint.created_date > cursor_date)
            | (
                (Complaint.created_date == cursor_date)
                & (Complaint.unique_key > cursor_key)
            )
        )

    stmt = stmt.limit(limit)
    rows = db.execute(stmt).scalars().all()

    next_cursor = None
    if len(rows) == limit:
        last = rows[-1]
        next_cursor = encode_cursor(last.created_date, last.unique_key)

    return rows, next_cursor