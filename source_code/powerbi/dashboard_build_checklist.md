# Power BI Dashboard Build Checklist

Save all PBIX files in this folder.

## Connection

- Server: `localhost:5432`
- Database: `bluestock_dw`
- Mode: Import
- Tables: all `dim_*` and `fact_*`

## Relationships

| From | Column | To | Column | Cardinality |
|---|---|---|---|---|
| fact_profit_loss | symbol | dim_company | symbol | Many-to-One |
| fact_profit_loss | year_id | dim_year | year_id | Many-to-One |
| fact_balance_sheet | symbol | dim_company | symbol | Many-to-One |
| fact_balance_sheet | year_id | dim_year | year_id | Many-to-One |
| fact_cash_flow | symbol | dim_company | symbol | Many-to-One |
| fact_cash_flow | year_id | dim_year | year_id | Many-to-One |
| fact_analysis | symbol | dim_company | symbol | Many-to-One |
| fact_ml_scores | symbol | dim_company | symbol | Many-to-One |
| fact_pros_cons | symbol | dim_company | symbol | Many-to-One |
| fact_documents | symbol | dim_company | symbol | Many-to-One |
| dim_company | sector | dim_sector | sector_name | Many-to-One |

Use single-direction filtering from dimensions to facts.

## Formatting Standard

- Primary: `#1F4E79`
- Secondary: `#2E75B6`
- Good: `#2ECC71`
- Warning: `#F39C12`
- Bad: `#E74C3C`
- Background: `#F8F9FA`
- Card background: `#FFFFFF`
- Font: Segoe UI
- Footer: `Data as of: [date]. For educational purposes only. Not financial advice.`

## Required Files

- `01_executive_overview.pbix`
- `02_company_deep_dive.pbix`
- `03_sector_comparison.pbix`
- `04_health_scorecard.pbix`
- `05_growth_analytics.pbix`
- `06_debt_leverage.pbix`
- `07_dividend_returns.pbix`

## Build Order

1. Executive Market Overview
2. Company Deep Dive
3. Sector Comparison Analyzer
4. Financial Health Scorecard
5. Growth & Valuation Analytics
6. Debt & Leverage Monitor
7. Dividend & Shareholder Returns

## Dashboard 1 - Executive Market Overview

Pages:

- Market Snapshot
- Sector Performance
- YoY Growth Tracker

Must include total companies, average ROE, excellent/weak health counts, sector distribution, health label distribution, top/bottom company rankings, OPM heatmap, revenue trend, profit trend, growth distribution, year slicer, and company slicer.

## Dashboard 2 - Company Deep Dive

Pages:

- Financial Summary
- Balance Sheet Health
- Cash Flow Analysis
- Growth & Returns Analysis

Every page must have a company slicer at the top.

## Dashboard 3 - Sector Comparison Analyzer

Pages:

- Sector vs Sector
- Companies Within a Sector
- Sector Trends Over Time

## Dashboard 4 - Financial Health Scorecard

Pages:

- Health Score Leaderboard
- Scorecard Breakdown

## Dashboard 5 - Growth & Valuation Analytics

Pages:

- Revenue & Profit Growth
- Margin Evolution
- EPS & Earnings Quality

## Dashboard 6 - Debt & Leverage Monitor

Pages:

- Leverage Snapshot
- Debt Trajectory

## Dashboard 7 - Dividend & Shareholder Returns

Pages:

- Dividend Analysis
- Shareholder Value
