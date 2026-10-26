
from dataguard.warehouse import connect


def profile_orders(rows: list[dict]) -> dict:
    """Check order records for common data-quality problems."""

    missing_order_ids = []
    missing_amounts = []
    duplicate_order_ids = []
    negative_amounts = []

    seen_order_ids = set()
    reported_duplicates = set()

    for row_number, row in enumerate(rows, start=1):
        order_id = row.get("order_id")
        amount = row.get("amount")

        if order_id is None or order_id == "":
            missing_order_ids.append(row_number)
        elif order_id in seen_order_ids:
            if order_id not in reported_duplicates:
                duplicate_order_ids.append(order_id)
                reported_duplicates.add(order_id)
        else:
            seen_order_ids.add(order_id)

        if amount is None or amount == "":
            missing_amounts.append(row_number)
        elif (
            isinstance(amount, (int, float))
            and not isinstance(amount, bool)
            and amount < 0
        ):
            negative_amounts.append(
                {"row": row_number, "amount": amount}
            )

    return {
        "records_checked": len(rows),
        "missing_order_ids": missing_order_ids,
        "missing_amounts": missing_amounts,
        "duplicate_order_ids": duplicate_order_ids,
        "negative_amounts": negative_amounts,
    }


def profile_database_orders() -> dict:
    """Load raw_orders from DuckDB and run the quality checks."""

    con = connect()
    try:
        result = con.execute("""
            SELECT order_id, amount
            FROM raw_orders
            ORDER BY order_id
        """).fetchall()

        rows = [
            {"order_id": row[0], "amount": row[1]}
            for row in result
        ]

        report = profile_orders(rows)
        report["source_table"] = "raw_orders"
        return report
    finally:
        con.close()


def profile_provider_amounts(anomaly_threshold: float = 10.0) -> dict:
    """Compare average order amounts across providers."""

    if anomaly_threshold <= 1:
        raise ValueError("anomaly_threshold must be greater than 1")

    con = connect()
    try:
        result = con.execute("""
            SELECT
                provider,
                COUNT(*) AS record_count,
                AVG(amount) AS average_amount,
                MIN(amount) AS minimum_amount,
                MAX(amount) AS maximum_amount,
                SUM(amount) AS total_amount
            FROM raw_orders
            GROUP BY provider
            ORDER BY provider
        """).fetchall()

        providers = [
            {
                "provider": row[0],
                "record_count": int(row[1]),
                "average_amount": float(row[2]) if row[2] is not None else None,
                "minimum_amount": float(row[3]) if row[3] is not None else None,
                "maximum_amount": float(row[4]) if row[4] is not None else None,
                "total_amount": float(row[5]) if row[5] is not None else None,
            }
            for row in result
        ]

        positive_averages = [
            item["average_amount"]
            for item in providers
            if item["average_amount"] is not None
            and item["average_amount"] > 0
        ]

        if not positive_averages:
            return {
                "source_table": "raw_orders",
                "anomaly_threshold": anomaly_threshold,
                "baseline_average_amount": None,
                "providers": providers,
                "anomalies": [],
                "message": "No positive provider averages are available.",
            }

        baseline = min(positive_averages)
        anomalies = []

        for item in providers:
            average = item["average_amount"]

            if average is not None and average >= baseline * anomaly_threshold:
                anomalies.append({
                    "provider": item["provider"],
                    "average_amount": average,
                    "baseline_average_amount": baseline,
                    "ratio_to_baseline": round(average / baseline, 2),
                    "reason": (
                        f"Provider average is at least {anomaly_threshold} "
                        "times the lowest positive provider average."
                    ),
                })

        return {
            "source_table": "raw_orders",
            "anomaly_threshold": anomaly_threshold,
            "baseline_average_amount": baseline,
            "providers": providers,
            "anomalies": anomalies,
        }
    finally:
        con.close()

  

