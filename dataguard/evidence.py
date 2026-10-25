
from dataclasses import dataclass, asdict
from math import isfinite
from typing import Iterable


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    evidence_type: str
    asset: str
    field: str
    statement: str
    measured_value: float | None = None

    def to_dict(self):
        return asdict(self)


def build_demo_evidence(asset: str, field: str, revenue_ratio: float) -> list[Evidence]:
    # This is fixture metadata for the learning demo, not a live DataHub response.
    return [
        Evidence(
            evidence_id=f"lineage-{asset}-{field}",
            evidence_type="lineage",
            asset=asset,
            field=field,
            statement="raw_orders.amount contributes to the revenue KPI.",
        ),
        Evidence(
            evidence_id=f"profile-{asset}-{field}",
            evidence_type="quantitative",
            asset=asset,
            field=field,
            statement="Current revenue differs materially from the healthy baseline.",
            measured_value=revenue_ratio,
        ),
    ]


def confirm_root_cause(
    asset: str,
    field: str,
    evidence_ids: Iterable[str],
    evidence_catalog: list[Evidence],
) -> dict:
    requested = set(evidence_ids)
    cited = [item for item in evidence_catalog if item.evidence_id in requested]

    if len(cited) != len(requested):
        return {"accepted": False, "reason": "One or more evidence IDs are unknown."}

    relevant = [item for item in cited if item.asset == asset and item.field == field]
    types = {item.evidence_type for item in relevant}
    if "lineage" not in types or "quantitative" not in types:
        return {
            "accepted": False,
            "reason": "Require both lineage and quantitative evidence for the same asset and field.",
        }

    quantitative = [
        item
        for item in relevant
        if item.evidence_type == "quantitative"
        and item.measured_value is not None
        and isfinite(item.measured_value)
    ]

    if not quantitative or max(
        abs(item.measured_value) for item in quantitative
    ) < 2:
        return {
            "accepted": False,
            "reason": (
                "Quantitative evidence is missing, non-finite, "
                "or does not meet the demo anomaly threshold."
            ),
        }

    return {
        "accepted": True,
        "asset": asset,
        "field": field,
        "evidence_ids": sorted(requested),
        "reason": "Required evidence types match the proposed asset and field.",
    }
