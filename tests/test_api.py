
from fastapi.testclient import TestClient

from dataguard.api import app

client = TestClient(app)


def test_health_endpoint_returns_success():
    response = client.get("/health")

    assert response.status_code == 200


def test_provider_quality_endpoint_returns_success():
    response = client.get("/quality/providers")

    assert response.status_code == 200

    data = response.json()

    assert data["source_table"] == "raw_orders"
    assert data["anomaly_threshold"] == 10.0
    assert "providers" in data
    assert "anomalies" in data


def test_provider_quality_rejects_invalid_threshold():
    response = client.get(
        "/quality/providers?anomaly_threshold=1"
    )

    assert response.status_code == 422


def test_confirmation_accepts_complete_evidence():
    response = client.post(
        "/confirm-root-cause",
        json={
            "asset": "raw_orders",
            "field": "amount",
            "evidence_ids": [
                "lineage-raw_orders-amount",
                "profile-raw_orders-amount",
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["accepted"] is True
    assert data["asset"] == "raw_orders"
    assert data["field"] == "amount"


def test_confirmation_rejects_incomplete_evidence():
    response = client.post(
        "/confirm-root-cause",
        json={
            "asset": "raw_orders",
            "field": "amount",
            "evidence_ids": [
                "lineage-raw_orders-amount",
            ],
        },
    )

    assert response.status_code == 422

    data = response.json()["detail"]

    assert data["accepted"] is False
    assert "both lineage and quantitative evidence" in data["reason"]


def test_investigation_summary_returns_quality_and_anomaly_reports():
    response = client.get("/investigation/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["asset"] == "raw_orders"
    
    finding = data["incident_finding"]

    assert finding["provider"] == "cloudpay_v2"
    assert finding["severity"] == "HIGH"
    assert "100 times the baseline" in finding["observation"]
    assert "Revenue metrics may be overstated" in finding["potential_impact"]
    assert "Verify provider amount units" in finding["recommended_action"]


    assert data["data_quality"]["records_checked"] == 200
    assert data["data_quality"]["missing_order_ids"] == []

    provider_report = data["provider_anomalies"]

    assert provider_report["source_table"] == "raw_orders"
    assert len(provider_report["anomalies"]) == 1
    assert provider_report["anomalies"][0]["provider"] == "cloudpay_v2"
    assert provider_report["anomalies"][0]["ratio_to_baseline"] == 100.0

def test_investigation_summary_flags_anomaly_at_threshold_50():
    response = client.get(
        "/investigation/summary?anomaly_threshold=50"
    )

    assert response.status_code == 200

    data = response.json()
    anomalies = data["provider_anomalies"]["anomalies"]

    assert len(anomalies) == 1
    assert anomalies[0]["provider"] == "cloudpay_v2"



def test_investigation_summary_has_no_anomaly_at_threshold_101():
    response = client.get(
        "/investigation/summary?anomaly_threshold=101"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["provider_anomalies"]["anomalies"] == []
    assert data["incident_finding"]["provider"] is None
    assert data["incident_finding"]["severity"] == "LOW"
    assert (
        data["incident_finding"]["observation"]
        == "No provider exceeded the configured anomaly threshold."
    )



