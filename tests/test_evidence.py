from dataguard.evidence import Evidence, build_demo_evidence, confirm_root_cause


def test_valid_lineage_and_quantitative_evidence_is_accepted():
    catalog = build_demo_evidence("raw_orders", "amount", 93.3)
    result = confirm_root_cause(
        "raw_orders",
        "amount",
        [item.evidence_id for item in catalog],
        catalog,
    )
    assert result["accepted"] is True


def test_missing_quantitative_evidence_is_rejected():
    catalog = build_demo_evidence("raw_orders", "amount", 93.3)
    result = confirm_root_cause(
        "raw_orders", "amount", [catalog[0].evidence_id], catalog
    )
    assert result["accepted"] is False


def test_evidence_for_wrong_field_is_rejected():
    catalog = build_demo_evidence("raw_orders", "amount", 93.3)
    result = confirm_root_cause(
        "raw_orders", "customer_id",
        [item.evidence_id for item in catalog], catalog
    )
    assert result["accepted"] is False


def test_unknown_evidence_id_is_rejected():
    catalog = build_demo_evidence("raw_orders", "amount", 93.3)
    result = confirm_root_cause(
        "raw_orders", "amount", ["invented-evidence"], catalog
    )
    assert result["accepted"] is False


def test_small_anomaly_is_rejected():
    catalog = build_demo_evidence("raw_orders", "amount", 1.1)
    result = confirm_root_cause(
        "raw_orders", "amount",
        [item.evidence_id for item in catalog], catalog
    )
    assert result["accepted"] is False
    
def test_anomaly_exactly_at_threshold_is_accepted():
    catalog = build_demo_evidence("raw_orders", "amount", 2.0)
    result = confirm_root_cause(
        "raw_orders",
        "amount",
        [item.evidence_id for item in catalog],
        catalog,
    )
    assert result["accepted"] is True


def test_negative_anomaly_uses_absolute_value():
    catalog = build_demo_evidence("raw_orders", "amount", -3.0)
    result = confirm_root_cause(
        "raw_orders",
        "amount",
        [item.evidence_id for item in catalog],
        catalog,
    )
    assert result["accepted"] is True


def test_quantitative_evidence_without_measurement_is_rejected():
    catalog = [
        Evidence(
            evidence_id="lineage-1",
            evidence_type="lineage",
            asset="raw_orders",
            field="amount",
            statement="Field contributes to revenue.",
        ),
        Evidence(
            evidence_id="profile-1",
            evidence_type="quantitative",
            asset="raw_orders",
            field="amount",
            statement="Anomaly measurement is missing.",
            measured_value=None,
        ),
    ]
    result = confirm_root_cause(
        "raw_orders",
        "amount",
        ["lineage-1", "profile-1"],
        catalog,
    )
    assert result["accepted"] is False


def test_evidence_for_wrong_asset_is_rejected():
    catalog = build_demo_evidence("raw_orders", "amount", 93.3)
    result = confirm_root_cause(
        "customers",
        "amount",
        [item.evidence_id for item in catalog],
        catalog,
    )
    assert result["accepted"] is False

