
import logging
import time
import uuid

from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel, Field

from .evidence import build_demo_evidence, confirm_root_cause
from .logging_config import configure_logging
from .quality import profile_database_orders, profile_provider_amounts
from .warehouse import revenue_summary

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DataGuard AI",
    description="Educational evidence-gated data incident response API",
    version="0.1.0",
)

BASELINE_REVENUE = 5500.0
CATALOG = build_demo_evidence("raw_orders", "amount", 93.3)


@app.middleware("http")
async def request_tracking_middleware(request: Request, call_next):
    # Accept only a simple, safe request ID from the caller.
    supplied_id = request.headers.get("X-Request-ID", "")
    if (
        supplied_id
        and len(supplied_id) <= 100
        and all(c.isalnum() or c in "-_." for c in supplied_id)
    ):
        request_id = supplied_id
    else:
        request_id = str(uuid.uuid4())

    request.state.request_id = request_id
    start_time = time.perf_counter()

    logger.info(
        "Request started | id=%s | method=%s | path=%s",
        request_id,
        request.method,
        request.url.path,
    )

    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Request failed | id=%s", request_id)
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id

    logger.info(
        "Request completed | id=%s | status=%s | duration_ms=%.2f",
        request_id,
        response.status_code,
        duration_ms,
    )

    return response


class ConfirmationRequest(BaseModel):
    asset: str = Field(min_length=1, max_length=200)
    field: str = Field(min_length=1, max_length=200)
    evidence_ids: list[str] = Field(min_length=1)


@app.get("/health")
def health():
    logger.info("Health check requested")
    return {"status": "ok"}


@app.get("/incident/demo")
def demo_incident():
    try:
        summary = revenue_summary()
    except Exception:
        logger.exception("Demo incident failed: warehouse unavailable")
        raise HTTPException(
            status_code=503,
            detail="Warehouse unavailable. Please try again later.",
        )

    ratio = summary["revenue"] / BASELINE_REVENUE

    return {
        "incident_id": "demo-revenue-anomaly",
        "status": "INVESTIGATION_REQUIRED",
        "summary": summary,
        "healthy_baseline_revenue": BASELINE_REVENUE,
        "revenue_ratio": round(ratio, 3),
        "note": (
            "Synthetic teaching fixture; the baseline is "
            "deliberately fixed for this demo."
        ),
    }


@app.get("/quality/demo")
def demo_data_quality():
    try:
        return profile_database_orders()
    except Exception:
        logger.exception("Data quality profiling failed")
        raise HTTPException(
            status_code=503,
            detail="Data quality profiling failed. Please try again later.",
        )


@app.get("/quality/providers")
def provider_quality(anomaly_threshold: float = Query(default=10.0, gt=1)):
    try:
        return profile_provider_amounts(
            anomaly_threshold=anomaly_threshold
        )
    except ValueError:
        logger.exception("Provider profiling rejected invalid input")
        raise HTTPException(
            status_code=400,
            detail="Invalid provider profiling parameters.",
        )
    except Exception:
        logger.exception("Provider profiling failed")
        raise HTTPException(
            status_code=503,
            detail="Provider profiling failed. Please try again later.",
        )


@app.post("/investigate/demo")
def investigate_demo():
    logger.info("Demo investigation requested")

    try:
        summary = revenue_summary()
    except Exception:
        logger.exception("Demo investigation failed: warehouse unavailable")
        raise HTTPException(
            status_code=503,
            detail="Warehouse unavailable. Please try again later.",
        )

    ratio = summary["revenue"] / BASELINE_REVENUE
    catalog = build_demo_evidence("raw_orders", "amount", ratio)

    logger.info(
        "Demo investigation completed: asset=raw_orders, "
        "field=amount, evidence_count=%s",
        len(catalog),
    )

    return {
        "asset": "raw_orders",
        "field": "amount",
        "evidence": [item.to_dict() for item in catalog],
        "next_step": (
            "Submit lineage and quantitative evidence IDs "
            "to /confirm-root-cause."
        ),
        "warning": (
            "Lineage is simulated fixture metadata in this milestone, "
            "not fetched from DataHub."
        ),
    }


@app.post("/confirm-root-cause")
def confirm(request: ConfirmationRequest):
    try:
        summary = revenue_summary()
    except Exception:
        logger.exception(
            "Root-cause confirmation failed: warehouse unavailable"
        )
        raise HTTPException(
            status_code=503,
            detail="Warehouse unavailable. Please try again later.",
        )

    ratio = summary["revenue"] / BASELINE_REVENUE
    catalog = build_demo_evidence("raw_orders", "amount", ratio)

    result = confirm_root_cause(
        request.asset,
        request.field,
        request.evidence_ids,
        catalog,
    )

    if not result["accepted"]:
        raise HTTPException(status_code=422, detail=result)

    return result


@app.get("/investigation/summary")
def investigation_summary(
    anomaly_threshold: float = Query(default=10.0, gt=1)
):
    try:
        quality_report = profile_database_orders()
        provider_report = profile_provider_amounts(
            anomaly_threshold=anomaly_threshold
        )

        anomalies = provider_report["anomalies"]

        if anomalies:
            flagged_provider = anomalies[0]
            ratio = flagged_provider["ratio_to_baseline"]

            if ratio >= 50:
                severity = "HIGH"
            elif ratio >= 10:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            incident_finding = {
                "provider": flagged_provider["provider"],
                "severity": severity,
                "observation": (
                    f"The provider average is "
                    f"{flagged_provider['ratio_to_baseline']:g} "
                    "times the baseline in the demo dataset."
                ),
                "potential_impact": (
                    "Revenue metrics may be overstated if transaction "
                    "amounts were recorded in cents instead of dollars."
                ),
                "recommended_action": (
                    "Verify provider amount units and transformation logic "
                    "before making production data changes."
                ),
            }
        else:
            incident_finding = {
                "provider": None,
                "severity": "LOW",
                "observation": (
                    "No provider exceeded the configured anomaly threshold."
                ),
                "potential_impact": (
                    "No provider anomaly was flagged by the current "
                    "threshold; this does not guarantee that the data "
                    "is correct."
                ),
                "recommended_action": (
                    "Review provider statistics and validate amount units "
                    "against the source system."
                ),
            }

        return {
            "status": "success",
            "asset": "raw_orders",
            "incident_finding": incident_finding,
            "data_quality": quality_report,
            "provider_anomalies": provider_report,
            "next_step": (
                "Review provider anomalies and gather matching "
                "lineage and quantitative evidence before "
                "confirming a root cause."
            ),
        }

    except Exception:
        logger.exception("Investigation summary failed")
        raise HTTPException(
            status_code=503,
            detail="Investigation summary failed. Please try again later.",
        )
