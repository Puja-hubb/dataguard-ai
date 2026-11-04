import duckdb

con = duckdb.connect(
    "data/dataguard.duckdb",
    read_only=True
)

BASELINE_PROVIDER = "cloudpay_v1"
THRESHOLD = 10

query = """
SELECT
    provider,
    COUNT(*) AS total_transactions,
    AVG(amount) AS average_amount,
    SUM(amount) AS total_revenue
FROM raw_orders
GROUP BY provider
"""

results = con.execute(query).fetchall()

provider_data = {
    row[0]: {
        "transactions": row[1],
        "average": row[2],
        "revenue": row[3]
    }
    for row in results
}

print("\nDATAGUARD AI - SAFE ANOMALY DETECTION")
print("=" * 50)

if BASELINE_PROVIDER not in provider_data:
    print("ERROR: Baseline provider not found!")

else:
    baseline = provider_data[BASELINE_PROVIDER]

    if baseline["transactions"] == 0:
        print("ERROR: Baseline has no transactions!")

    elif baseline["average"] is None or baseline["average"] <= 0:
        print("ERROR: Baseline average is invalid!")

    else:
        baseline_average = baseline["average"]

        for provider, data in provider_data.items():

            print(f"\nProvider: {provider}")

            if data["transactions"] == 0:
                print("STATUS: INSUFFICIENT DATA")
                continue

            if data["average"] is None or data["average"] < 0:
                print("STATUS: INVALID DATA")
                continue

            ratio = data["average"] / baseline_average

            print(f"Average: {data['average']}")
            print(f"Revenue: {data['revenue']}")
            print(f"Anomaly ratio: {ratio:.2f}x")

            if ratio >= THRESHOLD:
                print("STATUS: ANOMALY DETECTED!")
            else:
                print("STATUS: NORMAL")

con.close()