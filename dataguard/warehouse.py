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
