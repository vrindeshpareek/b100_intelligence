# Source Data Schema Notes

All monetary values are INR crores unless a column explicitly represents a percentage,
ratio, count, URL, label, or identifier. The ETL output uses `symbol` as the company key.

## companies

One row per company. Important fields are `symbol` (string key), `company_name`, logo and
website URLs, NSE/BSE URLs, `face_value`, `book_value`, `roce_pct`, and `roe_pct`.
Sector and sub-sector are supplied separately by `sector_mapping.csv` and merged into the
warehouse company dimension. Some URLs and descriptive text may be missing.

## profitandloss

One row per company and reporting period. Fields include sales, expenses, operating profit,
OPM%, other income, interest, depreciation, profit before tax, tax%, net profit, EPS, and
dividend payout%. ETL-derived fields are net profit margin, expense ratio, and interest
coverage. Early periods contain nulls, and division-derived values remain null when the
denominator is zero or missing.

## balancesheet

One row per company and reporting period. Fields include equity capital, reserves,
borrowings, other liabilities, total liabilities, fixed assets, CWIP, investments, other
assets, and total assets. ETL derives debt-to-equity and equity ratio. Borrowings for banks
include customer deposits and are not directly comparable with non-financial companies.

## cashflow

One row per company and reporting period. Fields include operating, investing, financing,
and net cash flow. ETL derives free cash flow and cash conversion ratio. Missing values are
preserved rather than converted to zero.

## analysis

One row per company and analysis horizon (`10Y`, `5Y`, or `3Y`). Fields are compounded sales
growth, compounded profit growth, stock-price CAGR, and ROE, all represented as percentages.

## prosandcons

Company observations with `is_pro`, category, text, source, confidence, and generation time.
Confidence is stored on a 0–1 scale. Text is free-form and may require presentation escaping.

## documents

Annual-report metadata keyed by company, fiscal year, and report URL. URLs may point to
third-party exchange filings and should be treated as external links.

## Normalized reporting-period fields

The clean financial files add `year_label`, `fiscal_year`, `quarter`, `is_ttm`,
`is_half_year`, and `sort_order`. Labels use `MMM YYYY`; `sort_order` controls chronology.
TTM rows are explicitly marked and must be excluded from historical growth and trend charts.

## Known quality rules

- Null values are expected, especially in early years, and must not be plotted as zero.
- Company and year uniqueness is enforced in warehouse fact tables where applicable.
- Balance-sheet totals and cash-flow identities are checked during warehouse loading.
- Percentage and ratio calculations guard against zero denominators.
- Company symbols are normalized to uppercase strings for joins.
