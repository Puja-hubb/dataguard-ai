# DataGuard AI

**A data quality and anomaly investigation platform built with Python, FastAPI, DuckDB, and pytest.**

DataGuard AI is an educational project that demonstrates how to investigate data-quality issues, detect unusual provider-level revenue patterns, and validate evidence submitted to support a root-cause claim.

The project currently uses synthetic data and deterministic rules. It is designed as a foundation for learning data engineering, backend development, data quality, and incident investigation workflows.

## Features

- Generate a reproducible synthetic orders dataset.
- Store and query data using DuckDB.
- Calculate revenue summaries and compare provider-level metrics.
- Detect unusual provider averages using a configurable anomaly threshold.
- Profile records for missing order IDs, missing amounts, duplicate order IDs, and negative amounts.
- Generate lineage and quantitative evidence for a data incident.
- Validate evidence against the expected asset and field.
- Expose data-quality and investigation functionality through a FastAPI REST API.
- Validate application behavior using automated pytest tests.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and data processing |
| FastAPI | REST API development |
| DuckDB | Analytical database |
| Pydantic | Request validation |
| pytest | Automated testing |
| Git and GitHub | Version control and project hosting |

## Architecture

DataGuard AI follows a simple flow: a client sends a request to the API, the application queries the data warehouse, and the relevant profiler or evidence-validation logic processes the request before returning a response.

```text
                 Client / API User
                         |
                         v
                FastAPI Application
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
        Data Quality  Provider     Evidence
          Profiler    Anomaly     Validation
                      Detection
             |           |           |
             +-----------+-----------+
                         |
                         v
                   DuckDB Database
                    (raw_orders)
                         |
                         v
                 Investigation Results
              Quality Reports and Evidence
```

### Component Responsibilities

- **FastAPI Application:** Exposes endpoints for health checks, incident investigation, data-quality reports, and root-cause evidence validation.
- **Data Quality Profiler:** Checks records for missing order IDs, missing amounts, duplicate IDs, and negative amounts.
- **Provider Anomaly Detection:** Compares provider-level average amounts to a baseline and flags unusually high values.
- **Evidence Validation:** Checks whether the submitted evidence meets the prototype's validation rules for a specified asset and field.
- **DuckDB Database:** Stores and queries the synthetic `raw_orders` dataset.
- **pytest:** Runs automated tests for API behavior, data-quality checks, and evidence-validation rules.

## Project Structure

```text
dataguard-ai-starter/
├── dataguard/
│   ├── __init__.py
│   ├── api.py
│   ├── evidence.py
│   ├── quality.py
│   ├── seed.py
│   └── warehouse.py
├── tests/
│   ├── test_api.py
│   ├── test_evidence.py
│   └── test_quality.py
├── data/
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

## Requirements

- Python 3.11 or newer
- `uv` (recommended) or `pip`

## Setup with uv

Run the following commands from the project directory:

```bash
uv venv
uv sync --extra dev
uv run python -m dataguard.seed
uv run uvicorn dataguard.api:app --reload
```

Open the following URL to explore the interactive API documentation:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Setup with pip

Create and activate a virtual environment.

For Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the project and development dependencies:

```bash
python -m pip install -e ".[dev]"
python -m dataguard.seed
python -m uvicorn dataguard.api:app --reload
```

## API Endpoints

The following endpoints are available in the current application:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check API health |
| GET | `/incident/demo` | Inspect the demonstration incident |
| GET | `/quality/demo` | Retrieve the demonstration quality report |
| GET | `/quality/providers` | Inspect provider-level anomaly statistics |
| POST | `/investigate/demo` | Generate investigation evidence |
| POST | `/confirm-root-cause` | Validate submitted evidence |
| GET | `/investigation/summary` | Retrieve a combined investigation summary |

### Example Root-Cause Confirmation Request

```json
{
  "asset": "raw_orders",
  "field": "amount",
  "evidence_ids": [
    "lineage-raw_orders-amount",
    "profile-raw_orders-amount"
  ]
}
```

Use the actual evidence IDs returned by your running API if they differ.

The evidence-validation workflow checks whether the submitted evidence meets the prototype's rules. Acceptance does not independently prove that a proposed root cause is correct.

## Run the Tests

With the virtual environment activated, run:

```powershell
python -m pytest
```

The current test suite contains 20 tests covering:

- API health and endpoint responses.
- Provider anomaly detection and threshold validation.
- Missing or mismatched investigation evidence.
- Evidence validation for the expected asset and field.
- Data-quality profiling.

The last recorded test run completed with **20 passed**. Run the tests again after making code changes to verify the current state.

## Example Data Scenario

The synthetic dataset contains two provider cohorts. One provider records amounts in normal units, while the other provider's amounts are multiplied by 100.

This creates a controlled anomaly that the application can detect using provider-level statistics.

The scenario demonstrates how data-quality checks can highlight suspicious metrics for further investigation.

## Safety and Limitations

- The dataset is synthetic and generated locally.
- Provider anomaly detection uses a simple statistical heuristic, not a production-calibrated baseline.
- Evidence validation checks identifiers, evidence types, and asset/field consistency; it is not a production security boundary.
- Evidence acceptance does not independently establish a true causal root cause.
- The project does not automatically repair data.
- The API currently has no authentication and should be used locally for development.
- No live DataHub integration, LLM-powered investigation, frontend, or automated production repair is implemented in this milestone.

## Future Improvements

Potential next steps include:

- Add stronger tests for edge cases and failure scenarios.
- Introduce historical baselines for anomaly detection.
- Add richer lineage and investigation evidence.
- Improve error handling and API validation.
- Add authentication and access control.
- Build a frontend for visualizing investigation results.
- Explore optional AI-assisted incident summaries with evidence-based safeguards.

## Learning Goals

This project provides hands-on practice with Python, REST API development, analytical SQL, data-quality profiling, anomaly detection, automated testing, and Git-based collaboration.

The goal is to build a reliable foundation that can be extended and explained clearly during technical interviews.