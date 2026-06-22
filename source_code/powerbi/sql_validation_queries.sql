-- Run these in DBeaver, pgAdmin, or psql to verify Power BI numbers.

SELECT COUNT(*) AS dim_company_rows FROM dim_company;
SELECT COUNT(*) AS fact_profit_loss_rows FROM fact_profit_loss;
SELECT COUNT(*) AS fact_balance_sheet_rows FROM fact_balance_sheet;
SELECT COUNT(*) AS fact_cash_flow_rows FROM fact_cash_flow;
SELECT COUNT(*) AS fact_analysis_rows FROM fact_analysis;
SELECT COUNT(*) AS fact_ml_scores_rows FROM fact_ml_scores;

SELECT MAX(fiscal_year) AS latest_fiscal_year
FROM dim_year
WHERE is_ttm = FALSE;

SELECT y.fiscal_year, SUM(pl.sales) AS total_sales
FROM fact_profit_loss pl
JOIN dim_year y ON y.year_id = pl.year_id
WHERE y.is_ttm = FALSE
GROUP BY y.fiscal_year
ORDER BY y.fiscal_year;

SELECT y.fiscal_year, SUM(pl.net_profit) AS total_net_profit
FROM fact_profit_loss pl
JOIN dim_year y ON y.year_id = pl.year_id
WHERE y.is_ttm = FALSE
GROUP BY y.fiscal_year
ORDER BY y.fiscal_year;

SELECT sector, COUNT(*) AS company_count
FROM dim_company
GROUP BY sector
ORDER BY company_count DESC;

SELECT c.sector, ROUND(AVG(pl.opm_pct), 2) AS avg_opm_pct
FROM fact_profit_loss pl
JOIN dim_company c ON c.symbol = pl.symbol
JOIN dim_year y ON y.year_id = pl.year_id
WHERE y.is_ttm = FALSE
GROUP BY c.sector
ORDER BY avg_opm_pct DESC;

SELECT c.symbol, c.company_name, c.sector, s.overall_score, s.health_label
FROM fact_ml_scores s
JOIN dim_company c ON c.symbol = s.symbol
ORDER BY s.overall_score DESC
LIMIT 20;

SELECT c.symbol, c.company_name, y.year_label, bs.debt_to_equity, pl.interest_coverage
FROM fact_balance_sheet bs
JOIN fact_profit_loss pl ON pl.symbol = bs.symbol AND pl.year_id = bs.year_id
JOIN dim_company c ON c.symbol = bs.symbol
JOIN dim_year y ON y.year_id = bs.year_id
WHERE y.is_ttm = FALSE
ORDER BY bs.debt_to_equity DESC NULLS LAST
LIMIT 20;

SELECT c.symbol, c.company_name, y.year_label, cf.operating_activity, pl.net_profit, cf.cash_conversion_ratio
FROM fact_cash_flow cf
JOIN fact_profit_loss pl ON pl.symbol = cf.symbol AND pl.year_id = cf.year_id
JOIN dim_company c ON c.symbol = cf.symbol
JOIN dim_year y ON y.year_id = cf.year_id
WHERE y.is_ttm = FALSE
ORDER BY cf.cash_conversion_ratio DESC NULLS LAST
LIMIT 20;
