import pytest

from dataguard import postgres


def test_connect_postgres_rejects_missing_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        postgres.connect_postgres()


def test_connect_postgres_uses_database_url(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://test:test@localhost:5432/test_db",
    )

    def fake_connect(database_url, connect_timeout):
        assert database_url == "postgresql://test:test@localhost:5432/test_db"
        assert connect_timeout == 5
        return "fake_connection"

    monkeypatch.setattr(postgres.psycopg, "connect", fake_connect)

    assert postgres.connect_postgres() == "fake_connection"


def test_get_postgres_provider_summary_returns_provider_statistics(monkeypatch):
    class FakeResult:
        def fetchall(self):
            return [
                ("cloudpay_v1", 8, 575.0, 4600.0),
                ("cloudpay_v2", 6, 51000.0, 306000.0),
            ]

    class FakeConnection:
        def __init__(self):
            self.closed = False

        def execute(self, query):
            assert "GROUP BY payment_provider" in query
            return FakeResult()

        def close(self):
            self.closed = True

    fake_connection = FakeConnection()
    monkeypatch.setattr(postgres, "connect_postgres", lambda: fake_connection)

    result = postgres.get_postgres_provider_summary()

    assert len(result) == 2
    assert result[0]["average_amount"] == 575.0
    assert result[1]["average_amount"] == 51000.0
    assert fake_connection.closed is True


def test_get_postgres_provider_summary_closes_connection_on_error(monkeypatch):
    class FakeConnection:
        def __init__(self):
            self.closed = False

        def execute(self, query):
            raise RuntimeError("Database query failed")

        def close(self):
            self.closed = True

    fake_connection = FakeConnection()
    monkeypatch.setattr(postgres, "connect_postgres", lambda: fake_connection)

    with pytest.raises(RuntimeError, match="Database query failed"):
        postgres.get_postgres_provider_summary()

    assert fake_connection.closed is True


def test_detect_postgres_anomalies_finds_high_average_provider(monkeypatch):
    providers = [
        {
            "payment_provider": "cloudpay_v1",
            "total_orders": 8,
            "average_amount": 575.0,
            "total_amount": 4600.0,
        },
        {
            "payment_provider": "cloudpay_v2",
            "total_orders": 6,
            "average_amount": 51000.0,
            "total_amount": 306000.0,
        },
    ]

    monkeypatch.setattr(
        postgres,
        "get_postgres_provider_summary",
        lambda: providers,
    )

    result = postgres.detect_postgres_anomalies()

    assert result["status"] == "anomaly_detected"
    assert result["reference_provider"] == "cloudpay_v1"
    assert len(result["findings"]) == 1
    assert result["findings"][0]["payment_provider"] == "cloudpay_v2"
    assert result["findings"][0]["ratio"] == pytest.approx(88.7)
    assert result["findings"][0]["severity"] == "high"


def test_detect_postgres_anomalies_returns_normal_when_no_anomaly(monkeypatch):
    providers = [
        {
            "payment_provider": "provider_a",
            "total_orders": 10,
            "average_amount": 100.0,
            "total_amount": 1000.0,
        },
        {
            "payment_provider": "provider_b",
            "total_orders": 10,
            "average_amount": 500.0,
            "total_amount": 5000.0,
        },
    ]

    monkeypatch.setattr(
        postgres,
        "get_postgres_provider_summary",
        lambda: providers,
    )

    result = postgres.detect_postgres_anomalies()

    assert result["status"] == "normal"
    assert result["findings"] == []


def test_detect_postgres_anomalies_handles_insufficient_providers(monkeypatch):
    providers = [
        {
            "payment_provider": "provider_a",
            "total_orders": 10,
            "average_amount": 100.0,
            "total_amount": 1000.0,
        }
    ]

    monkeypatch.setattr(
        postgres,
        "get_postgres_provider_summary",
        lambda: providers,
    )

    result = postgres.detect_postgres_anomalies()

    assert result["status"] == "insufficient_data"
    assert result["findings"] == []
    assert "At least two providers" in result["message"]


def test_detect_postgres_anomalies_handles_zero_reference_average(monkeypatch):
    providers = [
        {
            "payment_provider": "provider_zero",
            "total_orders": 10,
            "average_amount": 0.0,
            "total_amount": 0.0,
        },
        {
            "payment_provider": "provider_positive",
            "total_orders": 10,
            "average_amount": 100.0,
            "total_amount": 1000.0,
        },
    ]

    monkeypatch.setattr(
        postgres,
        "get_postgres_provider_summary",
        lambda: providers,
    )

    result = postgres.detect_postgres_anomalies()

    assert result["status"] == "normal"
    assert result["findings"] == []