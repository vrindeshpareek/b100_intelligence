# B100 Power BI DAX Measures Library

Create a dedicated table named `Measures` in Power BI, then add these measures.

## Core Counts

```DAX
Total Companies = DISTINCTCOUNT(dim_company[symbol])
```

```DAX
Latest Fiscal Year =
MAXX(
    FILTER(dim_year, dim_year[is_ttm] = FALSE()),
    dim_year[fiscal_year]
)
```

## Revenue And Profit

```DAX
Total Sales = SUM(fact_profit_loss[sales])
```

```DAX
Total Net Profit = SUM(fact_profit_loss[net_profit])
```

```DAX
Sales Latest Year =
VAR LatestYear = [Latest Fiscal Year]
RETURN
CALCULATE([Total Sales], dim_year[fiscal_year] = LatestYear, dim_year[is_ttm] = FALSE())
```

```DAX
Net Profit Latest Year =
VAR LatestYear = [Latest Fiscal Year]
RETURN
CALCULATE([Total Net Profit], dim_year[fiscal_year] = LatestYear, dim_year[is_ttm] = FALSE())
```

```DAX
YoY Sales Growth % =
VAR CurrentYear = MAX(dim_year[fiscal_year])
VAR CurrentSales = [Total Sales]
VAR PreviousSales =
    CALCULATE(
        [Total Sales],
        FILTER(ALL(dim_year), dim_year[fiscal_year] = CurrentYear - 1)
    )
RETURN
DIVIDE(CurrentSales - PreviousSales, PreviousSales) * 100
```

```DAX
YoY Profit Growth % =
VAR CurrentYear = MAX(dim_year[fiscal_year])
VAR CurrentProfit = [Total Net Profit]
VAR PreviousProfit =
    CALCULATE(
        [Total Net Profit],
        FILTER(ALL(dim_year), dim_year[fiscal_year] = CurrentYear - 1)
    )
RETURN
DIVIDE(CurrentProfit - PreviousProfit, PreviousProfit) * 100
```

## Margins And Returns

```DAX
Average OPM % = AVERAGE(fact_profit_loss[opm_pct])
```

```DAX
Average Net Profit Margin % = AVERAGE(fact_profit_loss[net_profit_margin_pct])
```

```DAX
Average Expense Ratio % = AVERAGE(fact_profit_loss[expense_ratio_pct])
```

```DAX
Average Interest Coverage = AVERAGE(fact_profit_loss[interest_coverage])
```

```DAX
ROE Last Year = AVERAGE(dim_company[roe_pct])
```

```DAX
ROCE Last Year = AVERAGE(dim_company[roce_pct])
```

```DAX
Average ROA % = AVERAGE(fact_profit_loss[return_on_assets])
```

```DAX
Average Asset Turnover = AVERAGE(fact_profit_loss[asset_turnover])
```

## Balance Sheet And Debt

```DAX
Total Borrowings = SUM(fact_balance_sheet[borrowings])
```

```DAX
Total Reserves = SUM(fact_balance_sheet[reserves])
```

```DAX
Total Assets = SUM(fact_balance_sheet[total_assets])
```

```DAX
Average Debt To Equity = AVERAGE(fact_balance_sheet[debt_to_equity])
```

```DAX
Average Equity Ratio % = AVERAGE(fact_balance_sheet[equity_ratio])
```

```DAX
Debt Free Flag =
VAR DTE = [Average Debt To Equity]
RETURN IF(NOT ISBLANK(DTE) && DTE < 0.1, 1, 0)
```

## Cash Flow

```DAX
Total Operating Cash Flow = SUM(fact_cash_flow[operating_activity])
```

```DAX
Total Investing Cash Flow = SUM(fact_cash_flow[investing_activity])
```

```DAX
Total Financing Cash Flow = SUM(fact_cash_flow[financing_activity])
```

```DAX
Total Free Cash Flow = SUM(fact_cash_flow[free_cash_flow])
```

```DAX
Average Cash Conversion Ratio = AVERAGE(fact_cash_flow[cash_conversion_ratio])
```

## Analysis CAGRs

```DAX
3Y Sales CAGR =
CALCULATE(
    AVERAGE(fact_analysis[compounded_sales_growth_pct]),
    fact_analysis[period_label] = "3Y"
)
```

```DAX
5Y Sales CAGR =
CALCULATE(
    AVERAGE(fact_analysis[compounded_sales_growth_pct]),
    fact_analysis[period_label] = "5Y"
)
```

```DAX
10Y Sales CAGR =
CALCULATE(
    AVERAGE(fact_analysis[compounded_sales_growth_pct]),
    fact_analysis[period_label] = "10Y"
)
```

```DAX
3Y Profit CAGR =
CALCULATE(
    AVERAGE(fact_analysis[compounded_profit_growth_pct]),
    fact_analysis[period_label] = "3Y"
)
```

```DAX
5Y Profit CAGR =
CALCULATE(
    AVERAGE(fact_analysis[compounded_profit_growth_pct]),
    fact_analysis[period_label] = "5Y"
)
```

```DAX
Stock CAGR 3Y =
CALCULATE(
    AVERAGE(fact_analysis[stock_price_cagr_pct]),
    fact_analysis[period_label] = "3Y"
)
```

## Health Scores

```DAX
Average Health Score = AVERAGE(fact_ml_scores[overall_score])
```

```DAX
Excellent Companies =
CALCULATE(
    DISTINCTCOUNT(fact_ml_scores[symbol]),
    fact_ml_scores[overall_score] >= 85
)
```

```DAX
Weak Poor Companies =
CALCULATE(
    DISTINCTCOUNT(fact_ml_scores[symbol]),
    fact_ml_scores[overall_score] < 50
)
```

```DAX
Profitability Score = AVERAGE(fact_ml_scores[profitability_score])
```

```DAX
Growth Score = AVERAGE(fact_ml_scores[growth_score])
```

```DAX
Leverage Score = AVERAGE(fact_ml_scores[leverage_score])
```

```DAX
Cash Flow Score = AVERAGE(fact_ml_scores[cashflow_score])
```

```DAX
Dividend Score = AVERAGE(fact_ml_scores[dividend_score])
```

```DAX
Trend Score = AVERAGE(fact_ml_scores[trend_score])
```

## Dividend

```DAX
Average Dividend Payout % = AVERAGE(fact_profit_loss[dividend_payout_pct])
```

```DAX
Average EPS = AVERAGE(fact_profit_loss[eps])
```

```DAX
Dividend Paid Years =
CALCULATE(
    DISTINCTCOUNT(dim_year[fiscal_year]),
    fact_profit_loss[dividend_payout_pct] > 0,
    dim_year[is_ttm] = FALSE()
)
```
