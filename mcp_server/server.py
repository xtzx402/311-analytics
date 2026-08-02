import os
from dotenv import load_dotenv
from mcp.server import MCPServer
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

mcp = MCPServer("NYC 311 Analytics")


@mcp.tool()
def query_complaints(
    borough: str = None,
    complaint_type: str = None,
    start_date: str = None,
    end_date: str = None,
    limit: int = 20,
) -> list[dict]:
    """Query NYC 311 complaints with optional filters (borough, complaint_type, date range)."""
    conditions = []
    params = {"limit": min(limit, 100)}

    if borough:
        conditions.append("borough = :borough")
        params["borough"] = borough
    if complaint_type:
        conditions.append("complaint_type = :complaint_type")
        params["complaint_type"] = complaint_type
    if start_date:
        conditions.append("created_date >= :start_date")
        params["start_date"] = start_date
    if end_date:
        conditions.append("created_date <= :end_date")
        params["end_date"] = end_date

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    with engine.connect() as conn:
        rows = conn.execute(text(f"""
            SELECT unique_key, created_date, complaint_type, descriptor, status, borough, agency
            FROM complaints
            {where_clause}
            ORDER BY created_date DESC
            LIMIT :limit
        """), params).all()

    return [dict(row._mapping) for row in rows]


@mcp.tool()
def get_stats_summary(year: int = None, complaint_type: str = None) -> dict:
    """Get aggregated statistics: total count, top complaint types, borough breakdown."""
    conditions = []
    params = {}

    if year:
        conditions.append("created_date >= :start_date AND created_date <= :end_date")
        params["start_date"] = f"{year}-01-01"
        params["end_date"] = f"{year}-12-31"
    if complaint_type:
        conditions.append("complaint_type = :complaint_type")
        params["complaint_type"] = complaint_type

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    with engine.connect() as conn:
        total = conn.execute(text(f"SELECT COUNT(*) FROM complaints {where_clause}"), params).scalar()

        by_type = conn.execute(text(f"""
            SELECT complaint_type, COUNT(*) as count FROM complaints {where_clause}
            GROUP BY complaint_type ORDER BY count DESC LIMIT 10
        """), params).all()

        by_borough = conn.execute(text(f"""
            SELECT borough, COUNT(*) as count FROM complaints
            {where_clause} {"AND" if where_clause else "WHERE"} borough IS NOT NULL
            GROUP BY borough ORDER BY count DESC
        """), params).all()

    return {
        "total": total,
        "by_type": [{"type": r[0], "count": r[1]} for r in by_type],
        "by_borough": [{"borough": r[0], "count": r[1]} for r in by_borough],
    }


@mcp.tool()
def get_complaint_types() -> list[str]:
    """List all distinct complaint types available in the dataset."""
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT DISTINCT complaint_type FROM complaints ORDER BY complaint_type")).all()
    return [r[0] for r in rows]


@mcp.tool()
def compare_periods(
    complaint_type: str = None,
    borough: str = None,
    period1_start: str = None,
    period1_end: str = None,
    period2_start: str = None,
    period2_end: str = None,
) -> dict:
    """Compare complaint counts between two time periods (e.g., this month vs last month)."""
    def count_in_range(start, end):
        conditions = ["created_date >= :start", "created_date <= :end"]
        params = {"start": start, "end": end}
        if complaint_type:
            conditions.append("complaint_type = :complaint_type")
            params["complaint_type"] = complaint_type
        if borough:
            conditions.append("borough = :borough")
            params["borough"] = borough
        with engine.connect() as conn:
            return conn.execute(
                text(f"SELECT COUNT(*) FROM complaints WHERE {' AND '.join(conditions)}"),
                params,
            ).scalar()

    count1 = count_in_range(period1_start, period1_end)
    count2 = count_in_range(period2_start, period2_end)
    change = count2 - count1
    pct_change = (change / count1 * 100) if count1 else None

    return {
        "period1": {"start": period1_start, "end": period1_end, "count": count1},
        "period2": {"start": period2_start, "end": period2_end, "count": count2},
        "change": change,
        "pct_change": round(pct_change, 1) if pct_change is not None else None,
    }


@mcp.tool()
def get_trending_complaint_types(borough: str = None, days: int = 30) -> list[dict]:
    """Find complaint types with the highest counts in the recent period."""
    conditions = ["created_date >= NOW() - (:days || ' days')::INTERVAL"]
    params = {"days": days}
    if borough:
        conditions.append("borough = :borough")
        params["borough"] = borough

    with engine.connect() as conn:
        rows = conn.execute(text(f"""
            SELECT complaint_type, COUNT(*) as count
            FROM complaints
            WHERE {' AND '.join(conditions)}
            GROUP BY complaint_type
            ORDER BY count DESC
            LIMIT 10
        """), params).all()

    return [{"type": r[0], "count": r[1]} for r in rows]


if __name__ == "__main__":
    mcp.run()