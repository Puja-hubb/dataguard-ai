
# DataGuard AI

**A data quality, anomaly detection, and investigation platform built with Python, FastAPI, DuckDB, and pytest.**

DataGuard AI is a portfolio project that demonstrates how to identify suspicious data patterns, profile data quality, collect investigation evidence, and maintain an investigation history through a REST API and an interactive web dashboard.

The application uses a synthetic orders dataset and deterministic validation rules to simulate a data incident in which one payment provider reports transaction amounts at a significantly different scale from the baseline.

The project demonstrates practical skills in backend development, data engineering, analytical SQL, API validation, automated testing, and Git-based development.

## Features

- **Synthetic data generation:** Generate a reproducible demonstration dataset of orders.
- **Analytical data storage:** Store and query order data using DuckDB.
- **Data quality profiling:** Check for missing order IDs, missing amounts, duplicate order IDs, and negative amounts.
- **Provider anomaly detection:** Compare provider-level average amounts against a baseline using a configurable threshold.
- **Incident analysis:** Compare baseline and current revenue to highlight unusual changes.
- **Investigation evidence:** Generate lineage and quantitative evidence for a selected data asset and field.
- **Evidence validation:** Validate submitted evidence against the expected asset, field, and supported evidence rules.
- **Investigation history:** Save and retrieve investigation records using DuckDB.
- **REST API:** Expose health, incident, data quality, and investigation functionality through FastAPI.
- **Interactive dashboard:** View API status, revenue metrics, data quality results, provider anomalies, and investigation history.
- **JSON report export:** Export an investigation report from the dashboard.
- **Automated testing:** Verify application behavior with pytest.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and data processing |
| FastAPI | REST API development |
| DuckDB | Analytical database and investigation history storage |
| Pydantic | Request data validation |
| SQL | Data queries and analytical operations |
| HTML, CSS, JavaScript | Interactive web dashboard |
| pytest | Automated testing |
| Git and GitHub | Version control and project hosting |

## Architecture

The application follows a simple data investigation workflow.

1. A user interacts with the dashboard or sends a request to the API.
2. FastAPI routes the request to the appropriate application logic.
3. The application queries the DuckDB warehouse and analyzes the demonstration data.
4. Data quality and anomaly detection logic identifies suspicious patterns.
5. Evidence validation checks investigation evidence against the requested asset and field.
6. Investigation records can be saved and retrieved from the investigation history.
7. The API returns results to the dashboard, where the user can review and export an investigation report.

```text
                    User / Dashboard
                           |
                           v
                    FastAPI Application
                           |
             +-------------+--------------+
             |             |              |
             v             v              v
       Data Quality    Anomaly         Evidence
        Profiling     Detection       Validation
             |             |              |
             +-------------+--------------+
                           |
                           v
                     DuckDB Warehouse
                           |
              +------------+------------+
              |                         |
              v                         v
        Synthetic Orders         Investigation
            Dataset                 History
                                        |
                                        v
                               Dashboard / JSON
                                  Report Export
```

## Project Structure

```text
dataguard-ai-starter/
├── dataguard/
│   ├── __init__.py
│   ├── api.py
│   ├── evidence.py
│   ├── quality.py
│   ├── seed.py
│   ├── warehouse.py
│   └── logging_config.py
├── frontend/
│   └── index.html
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
- Git
- A terminal such as Windows PowerShell
- `uv` or `pip` for Python dependency management

The project has been developed and tested in a Windows environment with a Python virtual environment.

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

### 3. Install the project

Using pip:

```powershell
python -m pip install -e ".[dev]"
```

Alternatively, if you use `uv` and the project's development dependency configuration:

```powershell
uv sync --extra dev
```

### 4. Generate the demonstration data

With the environment activated:

```powershell
python -m dataguard.seed
```

If you use `uv`, run:

```powershell
uv run python -m dataguard.seed
```

### 5. Start the API

With pip:

```powershell
python -m uvicorn dataguard.api:app --reload
```

Or with `uv`:

```powershell
uv run uvicorn dataguard.api:app --reload
```

### 6. Open the application

- **Interactive API documentation:** http://127.0.0.1:8000/docs
- **API health check:** http://127.0.0.1:8000/health
- **Web dashboard:** Open `frontend/index.html` in your browser while the API is running.

The dashboard sends requests to the local API. If the dashboard cannot connect, check that the API is running and review the browser console for errors.

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

The demonstration workflow simulates an issue in which transaction amounts from one provider are much larger than the baseline.

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

The second provider's average is approximately 100 times the baseline average. This controlled scenario allows the application to demonstrate how provider-level metrics can help identify suspicious data patterns.

The demonstration data is synthetic and does not represent real customer transactions.

## Run the Tests

Activate the project's virtual environment, then run:

```powershell
pytest -q
```

The automated test suite covers areas including:

- API health and endpoint responses.
- API request validation.
- Provider anomaly detection and threshold validation.
- Data quality profiling.
- Evidence validation and asset/field consistency.
- Investigation behavior and history retrieval.

**Latest verified test result: 36 passed, 1 warning.**

The warning was a Starlette deprecation notice concerning the use of `httpx` with its test client. It did not cause a test failure.

Run the tests again after changing the code to verify the current state.

## Safety and Limitations

DataGuard AI is an educational prototype, not a production incident management system.

- The dataset is synthetic and generated locally.
- Anomaly detection uses a simple heuristic rather than a production-calibrated statistical model.
- Lineage evidence is demonstration metadata; a live DataHub integration has not been implemented.
- Evidence validation checks prototype rules and does not establish definitive causality.
- The application does not automatically repair production data.
- The API does not currently provide authentication or role-based access control.
- The project does not currently use an LLM to conduct investigations.
- The JSON export provides a report file, not a digitally signed or independently verified audit record.

Do not expose the development API to untrusted networks without appropriate security controls.

## Future Improvements

Potential improvements include:

- Add historical baselines and more robust anomaly detection.
- Integrate a real data catalog and lineage service.
- Add richer investigation evidence and configurable rules.
- Improve structured logging, monitoring, and error handling.
- Add authentication and role-based access control.
- Introduce integration tests and additional edge-case coverage.
- Add dashboard filtering and more detailed investigation reports.
- Explore optional AI-assisted incident summaries grounded in verified evidence.
- Add deployment instructions and a hosted demonstration.

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

## Repository

GitHub: https://github.com/Puja-hubb/dataguard-ai

---

**Project status:** Educational portfolio project with a working API, dashboard, synthetic data analysis, investigation history, JSON report export, and an automated test suite.
