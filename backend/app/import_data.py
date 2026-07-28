import os
from datetime import datetime, timedelta
import time

import requests
from dotenv import load_dotenv
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import func, select

from database import SessionLocal, engine
from models import Complaint

load_dotenv()

APP_TOKEN = os.getenv("NYC_OPEN_DATA_APP_TOKEN")
BASE_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
PAGE_SIZE = 50000



def fetch_page(offset: int, since_date: str, max_retries: int = 5) -> list[dict]:
    params = {
        "$limit": PAGE_SIZE,
        "$offset": offset,
        "$where": f"created_date >= '{since_date}'",
        "$order": "created_date",
    }
    headers = {"X-App-Token": APP_TOKEN} if APP_TOKEN else {}

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(BASE_URL, params=params, headers=headers, timeout=120)
            resp.raise_for_status()
            return resp.json()
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            wait = 2 ** attempt
            print(f"Request failed (attempt {attempt}/{max_retries}): {e}. Retrying in {wait}s...")
            time.sleep(wait)

    raise RuntimeError(f"Failed to fetch offset={offset} after {max_retries} retries")


def parse_datetime(value: str | None):
    if not value:
        return None
    return datetime.fromisoformat(value)


def parse_record(raw: dict) -> dict | None:
    unique_key = raw.get("unique_key")
    if unique_key is None:
        return None

    lat = raw.get("latitude")
    lon = raw.get("longitude")
    location = None
    if lat and lon:
        point = Point(float(lon), float(lat))  # 注意顺序：Point(x=经度, y=纬度)
        location = from_shape(point, srid=4326)

    return {
        "unique_key": int(unique_key),
        "created_date": parse_datetime(raw.get("created_date")),
        "closed_date": parse_datetime(raw.get("closed_date")),
        "complaint_type": raw.get("complaint_type"),
        "descriptor": raw.get("descriptor"),
        "status": raw.get("status"),
        "borough": raw.get("borough"),
        "city": raw.get("city"),
        "latitude": float(lat) if lat else None,
        "longitude": float(lon) if lon else None,
        "incident_zip": raw.get("incident_zip"),
        "street_name": raw.get("street_name"),
        "location": location,
        "agency": raw.get("agency"),
        "agency_name": raw.get("agency_name"),
    }


def insert_batch(records: list[dict]):
    if not records:
        return
    stmt = pg_insert(Complaint).values(records)
    stmt = stmt.on_conflict_do_nothing(index_elements=["unique_key"])
    with engine.begin() as conn:
        conn.execute(stmt)

def get_last_created_date() -> datetime | None:
    with engine.connect() as conn:
        result = conn.execute(select(func.max(Complaint.created_date))).scalar()
    return result

def run_import(years_back: int = 3, max_pages: int | None = None):
    last_date = get_last_created_date()

    if last_date:
        since = last_date.strftime("%Y-%m-%dT%H:%M:%S.000")
        print(f"Resuming from last imported date: {since}")
    else:
        since = (datetime.now() - timedelta(days=years_back * 365)).strftime(
            "%Y-%m-%dT%H:%M:%S.000"
        )
        print(f"No existing data, starting fresh from: {since}")

    offset = 0
    total = 0
    page_count = 0

    while True:
        print(f"Fetching offset={offset} ...")
        page = fetch_page(offset=offset, since_date=since)
        if not page:
            print("No more records. Done.")
            break

        parsed = [r for r in (parse_record(row) for row in page) if r is not None]
        insert_batch(parsed)

        total += len(parsed)
        page_count += 1
        print(f"Inserted so far this run: {total}")

        if max_pages is not None and page_count >= max_pages:
            print(f"Reached max_pages={max_pages}, stopping (test mode).")
            break

        offset += PAGE_SIZE


if __name__ == "__main__":
    run_import(years_back=3)
