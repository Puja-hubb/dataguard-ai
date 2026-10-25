
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


