# B100 Intelligence

Fresh ready-to-run project for the B100 / Nifty financial intelligence system.

## What This Contains

- Python ETL pipeline for the 7 source tables.
- PostgreSQL 15 warehouse on `localhost:5432`.
- Star schema for Power BI.
- ML health scoring output.
- Django 4.2 web app and Django REST Framework API.
- Swagger docs at `/api/docs/`.

## Run From Scratch

```powershell
cd C:\Users\91950\Documents\b100_intelligence\source_code
copy config\.env.example config\.env
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
docker-compose up -d
```

Place the 7 Excel files in `data\raw\`:

```text
companies.xlsx
analysis.xlsx
balancesheet.xlsx
profitandloss.xlsx
cashflow.xlsx
prosandcons.xlsx
documents.xlsx
```

Then run:

```powershell
python run_etl.py --drop
cd django_app
python manage.py check
python manage.py runserver localhost:8000
```

Open:

- Website: http://localhost:8000/
- API docs: http://localhost:8000/api/docs/
- Power BI server: `localhost`
- Power BI database: `bluestock_dw`
- Power BI credentials: use the values from `config/.env`; do not save credentials in PBIX files

## Key API Endpoints

- `/api/companies/`
- `/api/companies/{SYMBOL}/snapshot/`
- `/api/companies/{SYMBOL}/timeseries/`
- `/api/profit-loss/`
- `/api/balance-sheet/`
- `/api/cash-flow/`
- `/api/analysis/`
- `/api/scores/`
- `/api/pros-cons/`
- `/api/documents/`
- `/api/market-summary/`

## Django Application

Required pages:

- `/` home, search, featured companies, sectors, insights
- `/companies/` filterable and sortable company table
- `/company/{symbol}/` company profile with eight Chart.js charts
- `/compare/` comparison for up to four companies
- `/screener/` ROE, debt, sector, health, and growth filters
- `/sector/{name}/` sector company view

Public REST API is under `/api/v1/`. JWT login is available at:

```text
POST /api/auth/token/
POST /api/auth/token/refresh/
```

Channel partner API is under `/api/partner/v1/` and requires:

```text
X-API-Key-ID
X-Timestamp
X-Signature
X-Nonce
```

After installing requirements, initialize Django-managed tables:

```powershell
cd django_app
python manage.py migrate
python manage.py createsuperuser
python manage.py create_test_partner --tier BASIC
python manage.py runserver localhost:8000
```

The API-key secret is displayed once. Use `api_management/hmac_example.py` as the signing example.

Run tests:

```powershell
cd ..
pytest --cov=django_app --cov-report=html
```

## Analytics Notebooks

The six assignments are in `notebooks/`. Install requirements into the same Python
environment used by Jupyter, then launch Jupyter from the repository root:

```powershell
python -m pip install -r requirements.txt
python -m jupyter notebook
```

Run notebooks in numeric order. Generated scores, anomaly flags, clusters, peer mappings,
and forecasts are written to `data/warehouse/`.

## Power BI Tables

Import all warehouse tables:

- `dim_company`
- `dim_year`
- `dim_sector`
- `dim_health_label`
- `fact_profit_loss`
- `fact_balance_sheet`
- `fact_cash_flow`
- `fact_analysis`
- `fact_ml_scores`
- `fact_pros_cons`
- `fact_documents`
