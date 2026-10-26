
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

    
def test_health_endpoint_returns_request_id():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")

    request_id = response.headers["X-Request-ID"]
    assert len(request_id) == 36


def test_request_tracking_preserves_valid_request_id():
    request_id = "test-request-123"

    response = client.get(
        "/health",
        headers={"X-Request-ID": request_id},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id


def test_request_tracking_replaces_invalid_request_id():
    invalid_id = "invalid request id!"

    response = client.get(
        "/health",
        headers={"X-Request-ID": invalid_id},
    )

    assert response.status_code == 200

    returned_id = response.headers["X-Request-ID"]
    assert returned_id != invalid_id
    assert len(returned_id) == 36


def test_incident_endpoint_does_not_expose_internal_error(monkeypatch):
    from dataguard import api

    secret_message = "database_password=super_secret"

    def failing_revenue_summary():
        raise RuntimeError(secret_message)

    monkeypatch.setattr(
        api,
        "revenue_summary",
        failing_revenue_summary,
    )

    response = client.get("/incident/demo")

    assert response.status_code == 503
    assert secret_message not in response.text
    assert response.json()["detail"] == (
        "Warehouse unavailable. Please try again later."
    )


def test_quality_endpoint_does_not_expose_internal_error(monkeypatch):
    from dataguard import api

    secret_message = "internal_database_path=C:\\private\\data"

    def failing_profile():
        raise RuntimeError(secret_message)

    monkeypatch.setattr(
        api,
        "profile_database_orders",
        failing_profile,
    )

    response = client.get("/quality/demo")

    assert response.status_code == 503
    assert secret_message not in response.text
    assert response.json()["detail"] == (
        "Data quality profiling failed. Please try again later."
    )

def test_confirm_rejects_whitespace_only_asset():
    response = client.post(
        "/confirm-root-cause",
        json={
            "asset": "   ",
            "field": "amount",
            "evidence_ids": ["lineage-raw_orders-amount"],
        },
    )

    assert response.status_code == 422


def test_confirm_rejects_whitespace_only_field():
    response = client.post(
        "/confirm-root-cause",
        json={
            "asset": "raw_orders",
            "field": "   ",
            "evidence_ids": ["lineage-raw_orders-amount"],
        },
    )

    assert response.status_code == 422


def test_confirm_rejects_empty_evidence_id():
    response = client.post(
        "/confirm-root-cause",
        json={
            "asset": "raw_orders",
            "field": "amount",
            "evidence_ids": ["   "],
        },
    )

    assert response.status_code == 422


def test_confirm_rejects_duplicate_evidence_ids():
    response = client.post(
        "/confirm-root-cause",
        json={
            "asset": "raw_orders",
            "field": "amount",
            "evidence_ids": [
                "lineage-raw_orders-amount",
                "lineage-raw_orders-amount",
            ],
        },
    )

    assert response.status_code == 422


def test_confirm_rejects_too_many_evidence_ids():
    response = client.post(
        "/confirm-root-cause",
        json={
            "asset": "raw_orders",
            "field": "amount",
            "evidence_ids": [
                f"evidence-{number}" for number in range(21)
            ],
        },
    )

    assert response.status_code == 422


def test_confirm_rejects_overlong_evidence_id():
    response = client.post(
        "/confirm-root-cause",
        json={
            "asset": "raw_orders",
            "field": "amount",
            "evidence_ids": ["x" * 201],
        },
    )

    assert response.status_code == 422


def test_investigation_endpoint_saves_history():
    investigation_response = client.post("/investigate/demo")

    assert investigation_response.status_code == 200

    history_response = client.get("/investigation/history")

    assert history_response.status_code == 200

    data = history_response.json()
    assert data["count"] >= 1

    latest = data["investigations"][0]
    assert latest["asset"] == "raw_orders"
    assert latest["field"] == "amount"
    assert latest["investigation_id"]
    assert latest["created_at"]
    assert len(latest["evidence"]) == 2


def test_investigation_history_respects_limit():
    first_response = client.post("/investigate/demo")
    second_response = client.post("/investigate/demo")

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    response = client.get("/investigation/history?limit=1")

    assert response.status_code == 200

    data = response.json()
    assert data["count"] == 1
    assert len(data["investigations"]) == 1


def test_investigation_history_rejects_invalid_limit():
    response = client.get("/investigation/history?limit=0")

    assert response.status_code == 422

def test_provider_quality_returns_503_when_profiling_fails(monkeypatch):
    from dataguard import api

    def failing_profile(anomaly_threshold=10.0):
        raise RuntimeError("internal database details")

    monkeypatch.setattr(
        api,
        "profile_provider_amounts",
        failing_profile,
    )

    response = client.get("/quality/providers")

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Provider profiling failed. Please try again later."
    )
    assert "internal database details" not in response.text


def test_investigation_returns_503_when_saving_history_fails(monkeypatch):
    from dataguard import api

    def failing_save(record):
        raise RuntimeError("internal database details")

    monkeypatch.setattr(api, "save_investigation", failing_save)

    response = client.post("/investigate/demo")

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Could not save investigation history. Please try again later."
    )
    assert "internal database details" not in response.text


def test_dashboard_serves_frontend_file():
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "DataGuard AI" in response.text


def test_dashboard_returns_500_when_frontend_file_is_missing(monkeypatch):
    from pathlib import Path
    from dataguard import api

    missing_file = Path("missing-dashboard-test.html")
    monkeypatch.setattr(api, "FRONTEND_FILE", missing_file)

    response = client.get("/")

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Dashboard file is unavailable."
    )

def test_investigation_history_returns_503_when_retrieval_fails(monkeypatch):
    from dataguard import api

    def failing_history(limit=20):
        raise RuntimeError("internal database details")

    monkeypatch.setattr(
        api,
        "get_investigation_history",
        failing_history,
    )

    response = client.get("/investigation/history")

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Investigation history is unavailable. Please try again later."
    )
    assert "internal database details" not in response.text

def test_investigation_returns_503_when_warehouse_is_unavailable(monkeypatch):
    from dataguard import api

    def failing_revenue_summary():
        raise RuntimeError("internal database details")

    monkeypatch.setattr(
        api,
        "revenue_summary",
        failing_revenue_summary,
    )

    response = client.post("/investigate/demo")

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Warehouse unavailable. Please try again later."
    )
    assert "internal database details" not in response.text

def test_provider_quality_returns_400_when_parameters_are_invalid(monkeypatch):
    from dataguard import api

    def failing_profile(anomaly_threshold):
        raise ValueError("internal validation details")

    monkeypatch.setattr(
        api,
        "profile_provider_amounts",
        failing_profile,
    )

    response = client.get("/quality/providers")

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Invalid provider profiling parameters."
    )
    assert "internal validation details" not in response.text

def test_confirm_returns_503_when_warehouse_is_unavailable(monkeypatch):
    from dataguard import api

    def failing_revenue_summary():
        raise RuntimeError("internal database details")

    monkeypatch.setattr(
        api,
        "revenue_summary",
        failing_revenue_summary,
    )

    response = client.post(
        "/confirm-root-cause",
        json={
            "asset": "raw_orders",
            "field": "amount",
            "evidence_ids": ["evidence-1"],
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Warehouse unavailable. Please try again later."
    )
    assert "internal database details" not in response.text

def test_investigation_summary_returns_503_when_profiling_fails(monkeypatch):
    from dataguard import api

    def failing_profile():
        raise RuntimeError("internal profiling details")

    monkeypatch.setattr(
        api,
        "profile_database_orders",
        failing_profile,
    )

    response = client.get("/investigation/summary")

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Investigation summary failed. Please try again later."
    )
    assert "internal profiling details" not in response.text

def test_investigation_summary_assigns_low_severity(monkeypatch):
    from dataguard import api

    monkeypatch.setattr(
        api,
        "profile_database_orders",
        lambda: {"status": "success"},
    )
    monkeypatch.setattr(
        api,
        "profile_provider_amounts",
        lambda anomaly_threshold: {
            "anomalies": [
                {
                    "provider": "Demo Provider",
                    "ratio_to_baseline": 5.0,
                }
            ]
        },
    )

    response = client.get("/investigation/summary")

    assert response.status_code == 200
    assert response.json()["incident_finding"]["severity"] == "LOW"
    assert response.json()["incident_finding"]["provider"] == "Demo Provider"

def test_investigation_summary_assigns_medium_severity(monkeypatch):
    from dataguard import api

    monkeypatch.setattr(
        api,
        "profile_database_orders",
        lambda: {"status": "success"},
    )
    monkeypatch.setattr(
        api,
        "profile_provider_amounts",
        lambda anomaly_threshold: {
            "anomalies": [
                {
                    "provider": "Demo Provider",
                    "ratio_to_baseline": 20.0,
                }
            ]
        },
    )

    response = client.get("/investigation/summary")

    assert response.status_code == 200
    assert response.json()["incident_finding"]["severity"] == "MEDIUM"

def test_demo_incident_returns_revenue_summary(monkeypatch):
    from dataguard import api

    monkeypatch.setattr(
        api,
        "revenue_summary",
        lambda: {"revenue": 5500.0},
    )

    response = client.get("/incident/demo")

    assert response.status_code == 200
    data = response.json()
    assert data["incident_id"] == "demo-revenue-anomaly"
    assert data["status"] == "INVESTIGATION_REQUIRED"
    assert data["summary"] == {"revenue": 5500.0}
    assert data["healthy_baseline_revenue"] == 5500.0
    assert data["revenue_ratio"] == 1.0

import asyncio

from starlette.requests import Request

from dataguard import api


def test_request_middleware_logs_and_reraises_exception():
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/test",
        "headers": [],
        "query_string": b"",
        "server": ("testserver", 80),
        "client": ("testclient", 1234),
        "scheme": "http",
    }
    request = Request(scope)

    async def failing_call_next(_request):
        raise RuntimeError("simulated request failure")

    async def run_test():
        try:
            await api.request_tracking_middleware(
                request,
                failing_call_next,
            )
        except RuntimeError as exc:
            assert str(exc) == "simulated request failure"
        else:
            raise AssertionError("Expected RuntimeError was not raised")

    asyncio.run(run_test())
