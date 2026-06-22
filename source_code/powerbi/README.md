# Power BI Connection Notes

Use PostgreSQL connector:

- Server: `localhost`
- Database: `bluestock_dw`
- Port: default `5432`
- User: `postgres`
- Password: `b100pass`

Relationships:

- `fact_profit_loss.symbol` -> `dim_company.symbol`
- `fact_profit_loss.year_id` -> `dim_year.year_id`
- `fact_balance_sheet.symbol` -> `dim_company.symbol`
- `fact_balance_sheet.year_id` -> `dim_year.year_id`
- `fact_cash_flow.symbol` -> `dim_company.symbol`
- `fact_cash_flow.year_id` -> `dim_year.year_id`
- `fact_analysis.symbol` -> `dim_company.symbol`
- `fact_ml_scores.symbol` -> `dim_company.symbol`
- `fact_pros_cons.symbol` -> `dim_company.symbol`
- `fact_documents.symbol` -> `dim_company.symbol`

Recommended first measures:

```DAX
Total Sales = SUM(fact_profit_loss[sales])
Total Net Profit = SUM(fact_profit_loss[net_profit])
Average OPM % = AVERAGE(fact_profit_loss[opm_pct])
Average Debt To Equity = AVERAGE(fact_balance_sheet[debt_to_equity])
Average Health Score = AVERAGE(fact_ml_scores[overall_score])
Company Count = DISTINCTCOUNT(dim_company[symbol])
```

Also use:

- `dax_measures.md`
- `dashboard_build_checklist.md`
- `sql_validation_queries.sql`
