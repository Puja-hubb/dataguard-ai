
import pytest

from dataguard import warehouse


def test_revenue_summary_raises_error_when_raw_orders_is_empty(
    monkeypatch, tmp_path
):
    # Use a temporary database instead of the project's real database.
    monkeypatch.setattr(warehouse, "DATA_DIR", tmp_path)
    monkeypatch.setattr(warehouse, "DB_PATH", tmp_path / "test.duckdb")

    # Create an empty raw_orders table.
    con = warehouse.connect()
    try:
        con.execute("""
            CREATE TABLE raw_orders (
                order_id INTEGER,
                provider VARCHAR,
                amount DOUBLE,
                event_date DATE
            )
        """)
    finally:
        con.close()

    # An empty table should raise a clear error.
    with pytest.raises(
        RuntimeError,
        match="raw_orders is empty; run `python -m dataguard.seed`",
    ):
        warehouse.revenue_summary()
