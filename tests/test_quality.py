
from dataguard.warehouse import reset_database
from dataguard.quality import profile_database_orders


def test_database_quality_profile_checks_real_table():
    reset_database()

    result = profile_database_orders()

    assert result["source_table"] == "raw_orders"
    assert result["records_checked"] == 200
    assert result["missing_order_ids"] == []
    assert result["missing_amounts"] == []
    assert result["duplicate_order_ids"] == []
    assert result["negative_amounts"] == []

import pytest

from dataguard.quality import profile_provider_amounts


def test_provider_profile_detects_cloudpay_v2_anomaly():
    from dataguard.warehouse import reset_database

    reset_database()
    result = profile_provider_amounts()

    assert result["source_table"] == "raw_orders"
    assert result["baseline_average_amount"] == pytest.approx(29.5)
    assert len(result["anomalies"]) == 1
    assert result["anomalies"][0]["provider"] == "cloudpay_v2"
    assert result["anomalies"][0]["ratio_to_baseline"] == pytest.approx(100.0)


def test_provider_profile_rejects_invalid_threshold():
    with pytest.raises(ValueError, match="greater than 1"):
        profile_provider_amounts(anomaly_threshold=1.0)

from dataguard.quality import profile_orders


def test_profile_orders_detects_missing_duplicate_and_negative_values():
    rows = [
        {"order_id": "A1", "amount": 100},
        {"order_id": "", "amount": None},
        {"order_id": "A1", "amount": -20},
        {"order_id": "A4", "amount": ""},
    ]

    report = profile_orders(rows)

    assert report["records_checked"] == 4
    assert report["missing_order_ids"] == [2]
    assert report["missing_amounts"] == [2, 4]
    assert report["duplicate_order_ids"] == ["A1"]
    assert report["negative_amounts"] == [
        {"row": 3, "amount": -20}
    ]


def test_profile_orders_empty_list():
    report = profile_orders([])

    assert report == {
        "records_checked": 0,
        "missing_order_ids": [],
        "missing_amounts": [],
        "duplicate_order_ids": [],
        "negative_amounts": [],
    }


def test_profile_orders_does_not_flag_boolean_as_negative_amount():
    report = profile_orders([
        {"order_id": "A1", "amount": True},
        {"order_id": "A2", "amount": False},
    ])

    assert report["negative_amounts"] == []
    assert report["missing_amounts"] == []

def test_provider_profile_handles_no_positive_averages(monkeypatch):
    from dataguard import quality

    class FakeResult:
        def fetchall(self):
            return [
                ("provider_zero", 2, 0.0, 0.0, 0.0, 0.0),
                ("provider_negative", 2, -5.0, -8.0, -2.0, -10.0),
                ("provider_null", 1, None, None, None, None),
            ]

    class FakeConnection:
        closed = False

        def execute(self, query):
            return FakeResult()

        def close(self):
            self.closed = True

    fake_connection = FakeConnection()
    monkeypatch.setattr(quality, "connect", lambda: fake_connection)

    result = quality.profile_provider_amounts()

    assert result["source_table"] == "raw_orders"
    assert result["baseline_average_amount"] is None
    assert result["anomalies"] == []
    assert result["message"] == "No positive provider averages are available."
    assert len(result["providers"]) == 3
    assert fake_connection.closed is True
    
def test_provider_profile_converts_values_and_flags_threshold_boundary(monkeypatch):
    from dataguard import quality

    class FakeResult:
        def fetchall(self):
            return [
                ("provider_a", 2, 10, 5, 15, 20),
                ("provider_b", 2, 100, 90, 110, 200),
                ("provider_null", 1, None, None, None, None),
            ]

    class FakeConnection:
        def __init__(self):
            self.closed = False

        def execute(self, query):
            return FakeResult()

        def close(self):
            self.closed = True

    fake_connection = FakeConnection()
    monkeypatch.setattr(quality, "connect", lambda: fake_connection)

    result = quality.profile_provider_amounts(anomaly_threshold=10)

    assert result["baseline_average_amount"] == 10.0
    assert result["providers"][0]["record_count"] == 2
    assert result["providers"][0]["average_amount"] == 10.0
    assert result["providers"][2]["average_amount"] is None
    assert result["anomalies"][0]["provider"] == "provider_b"
    assert result["anomalies"][0]["ratio_to_baseline"] == 10.0
    assert fake_connection.closed is True


def test_provider_profile_skips_null_average_when_checking_positive_averages(
    monkeypatch,
):
    from dataguard import quality

    class FakeResult:
        def fetchall(self):
            return [
                ("provider_null", 1, None, None, None, None),
                ("provider_positive", 2, 10.0, 5.0, 15.0, 20.0),
            ]

    class FakeConnection:
        def execute(self, query):
            return FakeResult()

        def close(self):
            pass

    monkeypatch.setattr(
        quality,
        "connect",
        lambda: FakeConnection(),
    )

    result = quality.profile_provider_amounts()

    assert result["baseline_average_amount"] == 10.0
    assert result["providers"][0]["average_amount"] is None
    assert result["anomalies"] == []

def test_duplicate_order_id_is_reported_only_once():
    from dataguard.quality import profile_orders

    rows = [
        {"order_id": "ORD-1", "amount": 10},
        {"order_id": "ORD-1", "amount": 20},
        {"order_id": "ORD-1", "amount": 30},
    ]

    result = profile_orders(rows)

    assert result["duplicate_order_ids"] == ["ORD-1"]
