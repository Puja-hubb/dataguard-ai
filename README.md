# DataGuard AI

**A data quality and anomaly investigation platform built with Python, FastAPI, DuckDB, and pytest.**

DataGuard AI is an educational project that demonstrates how to investigate data-quality issues, detect unusual provider-level revenue patterns, and require supporting evidence before accepting a root-cause claim.

This milestone is deterministic and uses synthetic data. It does not yet use an LLM, live DataHub integration, automatic SQL repair, GitHub automation, or a frontend.

## Features

- Generate a reproducible synthetic orders dataset.
- Store and query data using DuckDB.
- Summarize revenue and compare provider-level metrics.
- Detect unusually high provider averages using a configurable threshold.
- Profile records for missing order IDs, missing amounts, duplicate IDs, and negative amounts.
- Generate lineage and quantitative evidence for a data incident.
- Reject root-cause confirmation when required evidence is missing or refers to the wrong asset or field.
- Expose functionality through a FastAPI service.
- Run automated tests with pytest.

## Technology stack

- **Python** — application logic
- **FastAPI** — REST API
- **DuckDB** — analytical database
- **pytest** — automated testing
- **Pydantic** — request validation

## Requirements

- Python 3.11 or newer
- `uv` (recommended) or `pip`

## Setup with uv

From the project directory, run:

```bash
uv venv
uv sync --extra dev
uv run python -m dataguard.seed
uv run uvicorn dataguard.api:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to explore the interactive API documentation.

## Setup with pip

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Then install the project and development dependencies:

```bash
python -m pip install -e ".[dev]"
python -m dataguard.seed
python -m uvicorn dataguard.api:app --reload
```

## API walkthrough

Explore these endpoints in the interactive API documentation:

1. `GET /health` — check whether the API is running.
2. `GET /incident/demo` — inspect the demonstration incident.
3. `GET /quality/demo` — inspect the demonstration quality report.
4. `GET /quality/providers` — review provider-level anomaly statistics.
5. `POST /investigate/demo` — generate investigation evidence.
6. `POST /confirm-root-cause` — submit evidence IDs for validation.
7. `GET /investigation/summary` — view a combined quality and incident summary.

### Example root-cause confirmation request

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

Use the evidence IDs returned by your running API if they differ.

The evidence gate checks whether the submitted evidence meets the prototype's validation rules. Acceptance does not independently prove that the proposed root cause is true.

## Run the tests

With the project's virtual environment activated:

```powershell
python -m pytest
```

The current test suite contains 20 tests covering API behavior, evidence validation, and data-quality profiling.

## Project structure

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

## Safety and limitations

- The demonstration dataset is synthetic and generated locally.
- Provider anomaly detection uses a simple statistical heuristic, not a production-calibrated baseline.
- Evidence validation checks identifiers, evidence types, and asset/field consistency; it is not a production security boundary.
- The prototype does not automatically repair data.
- The API does not currently include authentication and should be run locally for development.

## Future improvements

Potential extensions include historical baselines, richer lineage integration, stronger anomaly detection, additional API tests, authentication, and a frontend for investigation reports.