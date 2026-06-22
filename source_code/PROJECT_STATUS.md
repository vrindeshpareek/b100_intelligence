# B100 Intelligence Project Status

Last verified: 2026-06-22

## Completed repository-side deliverables

- ETL scripts and warehouse schema are present.
- Cleaned raw-data outputs are present under `data/clean/`.
- Warehouse analytics exports are present under `data/warehouse/`:
  - `ml_scores.csv`
  - `anomaly_flags.csv`
  - `sector_clusters.csv`
  - `peer_mapping.csv`
  - `revenue_forecasts.csv`
- Source schema documentation is present at `data/schema_notes.md`.
- Six analytics notebooks are present under `notebooks/`.
- Django apps are present for companies, dashboard, accounts, ML engine, API, and API management.
- Required website routes are wired:
  - `/`
  - `/companies/`
  - `/company/{symbol}/`
  - `/compare/`
  - `/screener/`
  - `/sector/{name}/`
- Company detail chart endpoint and Chart.js client support the required eight chart types.
- Public REST API is wired under `/api/v1/`, including annual-report documents.
- Channel partner API is wired under `/api/partner/v1/`.
- HMAC authentication validates key ID, timestamp, nonce, body hash, and signature.
- HMAC signature comparison uses constant-time comparison.
- API secrets and webhook secrets are hashed/encrypted; plaintext is returned only at creation.
- Partner-tier throttling is implemented.
- Webhook dispatch signs outbound webhook payloads.
- Celery task wrappers are present for health scores and anomaly detection.
- Security hardening includes webhook URL validation and JWT login throttling.
- Formatting/lint configuration is present.

## Verification commands run

```powershell
python -m pytest --cov=django_app --cov-fail-under=75 -q
python django_app\manage.py check --settings=b100_site.test_settings
python -m flake8 django_app etl
python -m bandit -r django_app etl -q -ll
python -m safety check -r requirements.txt --full-report
```

Latest results:

- Tests: 16 passed.
- Coverage: 78.39%, above the 75% target.
- Django system check: no issues.
- Flake8: passed.
- Bandit: no failing medium/high issues; one static-table SQL `nosec` warning remains documented.
- Safety on project requirements: 0 reported vulnerabilities.

## User-owned/manual deliverables

The Power BI `.pbix` files are user-owned and were not modified. Their visual correctness,
relationships, slicers, refresh settings, and Power BI Service publishing must be verified
inside Power BI Desktop/Service.

Final demo activities are inherently manual:

- Walk through all seven Power BI dashboards.
- Run a live Django website demo.
- Run a sample public API request.
- Run a sample partner HMAC request.
- Present notebook/EDA insights.
