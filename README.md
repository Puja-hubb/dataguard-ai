# DataGuard AI — Starter

An independent educational implementation of evidence-gated data incident response.
This first milestone is intentionally deterministic: it does **not** yet use an LLM,
live DataHub, automatic SQL repair, GitHub publishing, or a frontend.

## Features in this milestone
- Generate a reproducible synthetic orders dataset.
- Store and query it with DuckDB.
- Compare current revenue with a healthy baseline.
- Produce quantitative evidence tied to a named asset and field.
- Reject root-cause confirmation when evidence is missing or refers to the wrong field.
- Expose a small FastAPI service and automated tests.

## Requirements
- Python 3.11 or newer
- `uv` (recommended) or `pip`

## Setup with uv
```bash
uv venv
uv sync --extra dev
uv run python -m dataguard.seed
uv run uvicorn dataguard.api:app --reload
```
Open http://127.0.0.1:8000/docs for the interactive API.

## Setup with pip
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m dataguard.seed
uvicorn dataguard.api:app --reload
```

## API walkthrough
1. `GET /health`
2. `GET /incident/demo` — shows the seeded anomaly and measured ratio.
3. `POST /investigate/demo` — produces evidence for the seeded incident.
4. `POST /confirm-root-cause` — submit evidence IDs returned by investigation.

Example request:
```json
{
  "asset": "raw_orders",
  "field": "amount",
  "evidence_ids": ["lineage-raw_orders-amount", "profile-raw_orders-amount"]
}
```
Use the actual evidence IDs returned by your running API if they differ.

## Tests
```bash
uv run pytest
```

## Project structure
```text
dataguard-ai/
├── dataguard/
│   ├── __init__.py
│   ├── api.py
│   ├── evidence.py
│   ├── warehouse.py
│   └── seed.py
├── tests/
│   └── test_evidence.py
├── data/
├── pyproject.toml
└── README.md
```

## Safety and limitations
- Dataset is synthetic and generated locally.
- The evidence gate checks that submitted evidence IDs exist, have the expected types,
  and identify the same asset and field. This is a learning prototype, not a production
  security boundary.
- No repair is performed in this milestone. Never connect experimental repair code to
  production databases or repositories.
- The API has no authentication and should only be run locally for now.
