from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "dataguard.duckdb"


def connect():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))


def revenue_summary() -> dict:
    con = connect()
    try:
        row = con.execute("""
            SELECT
                COUNT(*) AS row_count,
                SUM(amount) AS revenue,
                SUM(CASE WHEN provider = 'cloudpay_v2' THEN amount ELSE 0 END)
                    AS cloudpay_revenue,
                SUM(CASE WHEN provider <> 'cloudpay_v2' THEN amount ELSE 0 END)
                    AS other_revenue
            FROM raw_orders
        """).fetchone()
        if not row or row[0] == 0:
            raise RuntimeError("raw_orders is empty; run `python -m dataguard.seed`")
        return {
            "row_count": int(row[0]),
            "revenue": float(row[1]),
            "cloudpay_revenue": float(row[2]),
            "other_revenue": float(row[3]),
        }
    finally:
        con.close()


def reset_database() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = connect()
    try:
        con.execute("DROP TABLE IF EXISTS raw_orders")
        con.execute("""
            CREATE TABLE raw_orders (
                order_id INTEGER,
                provider VARCHAR,
                amount DOUBLE,
                event_date DATE
            )
        """)
        # Two provider cohorts, with cloudpay_v2 incorrectly sending cents.
        con.execute("""
            INSERT INTO raw_orders
            SELECT i, 'cloudpay_v1', 25.0 + (i % 10), DATE '2026-08-01'
            FROM range(1, 101) t(i)
        """)
        con.execute("""
            INSERT INTO raw_orders
            SELECT i + 1000, 'cloudpay_v2', (25.0 + (i % 10)) * 100,
                   DATE '2026-08-02'
            FROM range(1, 101) t(i)
        """)
    finally:
        con.close()

def save_investigation(record: dict) -> None:
    """Save an investigation report without modifying existing order data."""
    import json

    con = connect()
    try:
        con.execute("""
            CREATE TABLE IF NOT EXISTS investigation_history (
                investigation_id VARCHAR PRIMARY KEY,
                created_at VARCHAR NOT NULL,
                asset VARCHAR NOT NULL,
                field VARCHAR NOT NULL,
                evidence_json VARCHAR NOT NULL,
                next_step VARCHAR NOT NULL,
                warning VARCHAR NOT NULL
            )
        """)

        con.execute("""
            INSERT INTO investigation_history (
                investigation_id,
                created_at,
                asset,
                field,
                evidence_json,
                next_step,
                warning
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            record["investigation_id"],
            record["created_at"],
            record["asset"],
            record["field"],
            json.dumps(record["evidence"]),
            record["next_step"],
            record["warning"],
        ])
    finally:
        con.close()


def get_investigation_history(limit: int = 20) -> list[dict]:
    """Return the newest saved investigations first."""
    import json

    con = connect()
    try:
        con.execute("""
            CREATE TABLE IF NOT EXISTS investigation_history (
                investigation_id VARCHAR PRIMARY KEY,
                created_at VARCHAR NOT NULL,
                asset VARCHAR NOT NULL,
                field VARCHAR NOT NULL,
                evidence_json VARCHAR NOT NULL,
                next_step VARCHAR NOT NULL,
                warning VARCHAR NOT NULL
            )
        """)

        rows = con.execute("""
            SELECT
                investigation_id,
                created_at,
                asset,
                field,
                evidence_json,
                next_step,
                warning
            FROM investigation_history
            ORDER BY created_at DESC, investigation_id DESC
            LIMIT ?
        """, [limit]).fetchall()

        return [
            {
                "investigation_id": row[0],
                "created_at": row[1],
                "asset": row[2],
                "field": row[3],
                "evidence": json.loads(row[4]),
                "next_step": row[5],
                "warning": row[6],
            }
            for row in rows
        ]
    finally:
        con.close()
