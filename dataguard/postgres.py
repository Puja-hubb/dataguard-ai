import os
import psycopg


def connect_postgres():
    """Connect to PostgreSQL using a secure environment variable."""

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not configured."
        )

    return psycopg.connect(
        database_url,
        connect_timeout=5,
    )


def get_postgres_provider_summary():
    """Return transaction statistics grouped by payment provider."""

    conn = connect_postgres()

    try:
        rows = conn.execute(
            """
            SELECT
                payment_provider,
                COUNT(*) AS total_orders,
                AVG(amount) AS average_amount,
                SUM(amount) AS total_amount
            FROM orders
            GROUP BY payment_provider
            ORDER BY payment_provider
            """
        ).fetchall()

        return [
            {
                "payment_provider": row[0],
                "total_orders": row[1],
                "average_amount": float(row[2]),
                "total_amount": float(row[3]),
            }
            for row in rows
        ]

    finally:
        conn.close()


def detect_postgres_anomalies():
    """Detect providers with unusually high average transaction amounts."""

    providers = get_postgres_provider_summary()

    if len(providers) < 2:
        return {
            "status": "insufficient_data",
            "message": "At least two providers are required for comparison.",
            "findings": [],
        }

    reference = min(
        providers,
        key=lambda provider: provider["average_amount"],
    )

    findings = []

    for provider in providers:
        if provider["payment_provider"] == reference["payment_provider"]:
            continue

        ratio = (
            provider["average_amount"] / reference["average_amount"]
            if reference["average_amount"] > 0
            else None
        )

        if ratio is not None and ratio > 10:
            findings.append({
                "payment_provider": provider["payment_provider"],
                "average_amount": provider["average_amount"],
                "reference_provider": reference["payment_provider"],
                "reference_average": reference["average_amount"],
                "ratio": round(ratio, 2),
                "severity": "high",
                "message": "Average transaction amount is unusually high.",
            })

    return {
        "status": "anomaly_detected" if findings else "normal",
        "reference_provider": reference["payment_provider"],
        "findings": findings,
    }