# DataGuard AI

**An Evidence-Gated Data Reliability and Incident Investigation Platform**

DataGuard AI is an educational full-stack data reliability application designed to demonstrate how data quality monitoring, provider-level anomaly detection, and evidence-based incident investigation can work together.

The application uses Python, FastAPI, DuckDB, SQL, and a browser-based dashboard to inspect synthetic transaction data, identify unusual provider-level patterns, validate investigation evidence, and generate investigation reports.

**Live Demo:** https://dataguard-ai-u2px.onrender.com/

**API Documentation:** https://dataguard-ai-u2px.onrender.com/docs

**GitHub Repository:** https://github.com/Puja-hubb/dataguard-ai

---

## Features

- **Data Quality Monitoring:** Checks transaction records for missing IDs, missing amounts, duplicate IDs, and negative amounts.
- **Provider-Level Anomaly Detection:** Compares average transaction amounts across payment providers.
- **Analytical SQL:** Uses DuckDB to query and analyze transaction data.
- **Incident Investigation:** Generates evidence for unusual revenue patterns.
- **Evidence Validation:** Checks evidence types, asset and field consistency, measurement validity, and configured thresholds.
- **Investigation History:** Stores and retrieves investigation records.
- **Investigation Summary:** Combines provider anomaly information and investigation recommendations.
- **Interactive Dashboard:** Provides a browser-based interface for monitoring and investigation.
- **JSON Report Export:** Exports investigation results and associated evidence.
- **Standalone Database Inspection:** Provides a read-only Python script for inspecting provider-level statistics.
- **REST API:** Exposes application functionality through FastAPI endpoints.
- **Automated Testing:** Includes tests for API behavior, evidence validation, data quality, database seeding, and warehouse operations.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend application development |
| FastAPI | REST API framework |
| DuckDB | Analytical database |
| SQL | Data aggregation and analysis |
| HTML, CSS, JavaScript | Interactive frontend dashboard |
| Pydantic | Request validation and data models |
| pytest | Automated testing |
| uv / pip | Dependency management |
| Git and GitHub | Version control and source code management |
| Render | Cloud deployment |

## Architecture

```text
                  User
                   |
                   v
          Web Dashboard
       HTML / CSS / JavaScript
                   |
                   v
              FastAPI
                   |
        +----------+----------+
        |          |          |
        v          v          v
    Data Quality  Provider  Investigation
      Profiling   Analysis    Evidence
        |          |          |
        +----------+----------+
                   |
                   v
                DuckDB
                   |
                   v
             raw_orders
            Synthetic Data
```

The standalone database inspection script also reads the DuckDB database directly in read-only mode.

## Project Structure

```text
dataguard-ai/
|
|-- dataguard/
|   |-- __init__.py
|   |-- api.py
|   |-- evidence.py
|   |-- inspect_database.py
|   |-- logging_config.py
|   |-- quality.py
|   |-- seed.py
|   |-- warehouse.py
|
|-- frontend/
|   |-- index.html
|
|-- tests/
|   |-- test_api.py
|   |-- test_evidence.py
|   |-- test_quality.py
|   |-- test_seed.py
|   |-- test_warehouse.py
|
|-- data/                  # Generated local database
|-- .gitignore
|-- pyproject.toml
|-- uv.lock
|-- README.md
```

## Requirements

- Python 3.11 or newer
- Git
- A terminal such as Windows PowerShell
- `uv` or `pip` for Python dependency management

The project has been developed and tested in a Windows environment using Python 3.14.6.

## Setup and Run

### 1. Clone the repository

```powershell
git clone https://github.com/Puja-hubb/dataguard-ai.git
cd dataguard-ai
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, follow your system's Python environment guidance rather than changing execution policies without understanding the implications.

### 3. Install dependencies

Using pip:

```powershell
python -m pip install -e ".[dev]"
```

Alternatively, using uv:

```powershell
uv sync --extra dev
```

### 4. Generate demonstration data

With the virtual environment activated:

```powershell
python -m dataguard.seed
```

Alternatively, using uv:

```powershell
uv run python -m dataguard.seed
```

This initializes the local DuckDB database and generates synthetic transaction records.

### 5. Start the API

Using pip:

```powershell
python -m uvicorn dataguard.api:app --reload
```

Or using uv:

```powershell
uv run uvicorn dataguard.api:app --reload
```

### 6. Open the application

- **Interactive API documentation:** http://127.0.0.1:8000/docs
- **API health check:** http://127.0.0.1:8000/health
- **Web dashboard:** http://127.0.0.1:8000/

The FastAPI application serves the frontend dashboard. Make sure the API is running before opening the dashboard.

### 7. Run standalone database inspection

```powershell
python -m dataguard.inspect_database
```

This script opens the DuckDB database in read-only mode, calculates provider-level transaction statistics, and compares provider averages against a configured baseline.

It uses `cloudpay_v1` as the baseline and a 10x anomaly threshold.

## Live Deployment

DataGuard AI is deployed using Render.

| Resource | Link |
|---|---|
| Live Dashboard | https://dataguard-ai-u2px.onrender.com/ |
| API Documentation | https://dataguard-ai-u2px.onrender.com/docs |
| API Health Check | https://dataguard-ai-u2px.onrender.com/health |
| GitHub Repository | https://github.com/Puja-hubb/dataguard-ai |

The deployed service initializes its demonstration database during startup.

**Deployment note:** The hosted application uses a demonstration environment. Its local database and investigation history should not be treated as durable production storage. Data may be reset when the service restarts or is redeployed.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check API health |
| GET | `/incident/demo` | Inspect the demonstration incident |
| GET | `/quality/demo` | Retrieve the demonstration data quality report |
| GET | `/quality/providers` | Inspect provider-level anomaly statistics |
| POST | `/investigate/demo` | Generate investigation evidence and save an investigation record |
| POST | `/confirm-root-cause` | Validate submitted investigation evidence |
| GET | `/investigation/summary` | Retrieve a combined investigation summary |
| GET | `/investigation/history` | Retrieve saved investigation records |

Use the interactive API documentation at `/docs` to inspect request schemas, submit requests, and review actual responses.

## Example Investigation Workflow

The demonstration workflow simulates an issue in which transaction amounts from one provider are significantly larger than the baseline.

The dashboard can be used to:

1. Review the current API status.
2. Inspect revenue metrics and data quality results.
3. Identify provider-level anomalies.
4. Run an investigation and review the returned evidence.
5. View saved investigation history.
6. Export an investigation report as a JSON file.

### Example root-cause confirmation request

The following illustrates the general structure of a request. Use evidence IDs returned by the running API.

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

This is an illustrative payload. The actual evidence IDs and accepted values depend on the response and validation rules of the running application.

Evidence validation indicates whether submitted evidence satisfies the prototype's rules. It does not independently prove that a proposed root cause is factually correct.

## Example Data Scenario

The synthetic dataset contains two provider cohorts:

- `cloudpay_v1` represents the baseline provider with an average transaction amount of approximately `29.5`.
- `cloudpay_v2` represents an anomalous provider with an average transaction amount of approximately `2950`.

The second provider's average is approximately 100 times the baseline average.

This controlled scenario allows the application to demonstrate how provider-level metrics can help identify suspicious data patterns.

The demonstration data is synthetic and does not represent real customer transactions.

## Run the Tests

Activate the project's virtual environment, then run:

```powershell
python -m pytest -v
```

The automated test suite covers:

- API health and endpoint responses.
- API request validation.
- Provider anomaly detection and threshold validation.
- Data quality profiling.
- Evidence validation and asset/field consistency.
- Investigation behavior and history retrieval.
- Database seeding and reset behavior.
- Warehouse operations.

### Latest Verified Test Results

**62 passed, 1 warning in 2.66s**

All 62 collected tests passed successfully.

The single non-failing warning is a Python `runpy` RuntimeWarning associated with `dataguard.seed` already being present in `sys.modules` when the module is executed as a script. It did not cause any test failures.

Run the tests again after changing the code to verify the current state.

## Safety and Limitations

DataGuard AI is an educational prototype, not a production incident management system.

- The dataset is synthetic and generated locally.
- Anomaly detection uses a simple heuristic rather than a production-calibrated statistical model.
- The standalone inspection script uses a fixed baseline provider and threshold.
- Lineage evidence is demonstration metadata; a live DataHub integration has not been implemented.
- Evidence validation checks prototype rules and does not establish definitive causality.
- The application does not automatically repair production data.
- The API does not currently provide authentication or role-based access control.
- The project does not currently use an LLM to conduct investigations.
- The JSON export provides a report file, not a digitally signed or independently verified audit record.
- The hosted demonstration does not guarantee durable database or investigation-history persistence.

Do not expose the development API to untrusted networks without appropriate security controls.

## Future Improvements

Potential improvements include:

- Add historical baselines and more robust anomaly detection.
- Integrate a real data catalog and lineage service.
- Add richer investigation evidence and configurable rules.
- Improve structured logging, monitoring, and error handling.
- Add authentication and role-based access control.
- Expand integration tests and edge-case coverage.
- Add dashboard filtering and more detailed investigation reports.
- Explore optional AI-assisted incident summaries grounded in verified evidence.
- Introduce persistent production-grade database storage.
- Add deployment monitoring and automated CI/CD workflows.

## Learning Outcomes

This project provides practical experience with:

- Python application development.
- REST API design with FastAPI.
- Analytical SQL and DuckDB.
- Data quality profiling and anomaly detection.
- Request validation and evidence-based workflows.
- Automated testing with pytest.
- Frontend integration with a backend API.
- Git, GitHub, and iterative development.
- Cloud deployment using Render.
- Working with synthetic analytical datasets.

## Repository

GitHub: https://github.com/Puja-hubb/dataguard-ai

---

**Project Status:** Educational portfolio project with a deployed API, interactive dashboard, synthetic data analysis, provider-level anomaly detection, evidence validation, investigation history, JSON report export, standalone database inspection, and an automated test suite.