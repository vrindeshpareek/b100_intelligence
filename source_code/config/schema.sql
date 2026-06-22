CREATE TABLE IF NOT EXISTS dim_sector (
    sector_id SERIAL PRIMARY KEY,
    sector_name VARCHAR(100) NOT NULL UNIQUE,
    sector_code VARCHAR(20),
    description TEXT
);

CREATE TABLE IF NOT EXISTS dim_company (
    symbol VARCHAR(20) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    sub_sector VARCHAR(100),
    company_logo TEXT,
    website TEXT,
    nse_url TEXT,
    bse_url TEXT,
    face_value NUMERIC(12,2),
    book_value NUMERIC(12,2),
    about_company TEXT,
    chart_link TEXT,
    roce_pct NUMERIC(10,4),
    roe_pct NUMERIC(10,4)
);

CREATE TABLE IF NOT EXISTS dim_year (
    year_id SERIAL PRIMARY KEY,
    year_label VARCHAR(30) NOT NULL UNIQUE,
    fiscal_year INT,
    quarter VARCHAR(5),
    is_ttm BOOLEAN DEFAULT FALSE,
    is_half_year BOOLEAN DEFAULT FALSE,
    sort_order INT
);

CREATE TABLE IF NOT EXISTS dim_health_label (
    label_id SERIAL PRIMARY KEY,
    label_name VARCHAR(20) NOT NULL UNIQUE,
    min_score NUMERIC(5,2),
    max_score NUMERIC(5,2),
    color_hex VARCHAR(7)
);

CREATE TABLE IF NOT EXISTS fact_profit_loss (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL REFERENCES dim_company(symbol),
    year_id INT NOT NULL REFERENCES dim_year(year_id),
    sales NUMERIC(18,2),
    expenses NUMERIC(18,2),
    operating_profit NUMERIC(18,2),
    opm_pct NUMERIC(10,4),
    other_income NUMERIC(18,2),
    interest NUMERIC(18,2),
    depreciation NUMERIC(18,2),
    profit_before_tax NUMERIC(18,2),
    tax_pct NUMERIC(10,4),
    net_profit NUMERIC(18,2),
    eps NUMERIC(12,4),
    dividend_payout_pct NUMERIC(10,4),
    net_profit_margin_pct NUMERIC(10,4),
    expense_ratio_pct NUMERIC(10,4),
    interest_coverage NUMERIC(12,4),
    asset_turnover NUMERIC(12,4),
    return_on_assets NUMERIC(12,4),
    UNIQUE(symbol, year_id)
);

CREATE TABLE IF NOT EXISTS fact_balance_sheet (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL REFERENCES dim_company(symbol),
    year_id INT NOT NULL REFERENCES dim_year(year_id),
    equity_capital NUMERIC(18,2),
    reserves NUMERIC(18,2),
    borrowings NUMERIC(18,2),
    other_liabilities NUMERIC(18,2),
    total_liabilities NUMERIC(18,2),
    fixed_assets NUMERIC(18,2),
    cwip NUMERIC(18,2),
    investments NUMERIC(18,2),
    other_assets NUMERIC(18,2),
    total_assets NUMERIC(18,2),
    debt_to_equity NUMERIC(12,4),
    equity_ratio NUMERIC(10,4),
    UNIQUE(symbol, year_id)
);

CREATE TABLE IF NOT EXISTS fact_cash_flow (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL REFERENCES dim_company(symbol),
    year_id INT NOT NULL REFERENCES dim_year(year_id),
    operating_activity NUMERIC(18,2),
    investing_activity NUMERIC(18,2),
    financing_activity NUMERIC(18,2),
    net_cash_flow NUMERIC(18,2),
    free_cash_flow NUMERIC(18,2),
    cash_conversion_ratio NUMERIC(12,4),
    UNIQUE(symbol, year_id)
);

CREATE TABLE IF NOT EXISTS fact_analysis (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL REFERENCES dim_company(symbol),
    period_label VARCHAR(10) NOT NULL,
    compounded_sales_growth_pct NUMERIC(10,4),
    compounded_profit_growth_pct NUMERIC(10,4),
    stock_price_cagr_pct NUMERIC(10,4),
    roe_pct NUMERIC(10,4),
    UNIQUE(symbol, period_label)
);

CREATE TABLE IF NOT EXISTS fact_ml_scores (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL REFERENCES dim_company(symbol),
    computed_at TIMESTAMP DEFAULT NOW(),
    overall_score NUMERIC(6,2),
    profitability_score NUMERIC(6,2),
    growth_score NUMERIC(6,2),
    leverage_score NUMERIC(6,2),
    cashflow_score NUMERIC(6,2),
    dividend_score NUMERIC(6,2),
    trend_score NUMERIC(6,2),
    health_label VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS fact_pros_cons (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL REFERENCES dim_company(symbol),
    is_pro BOOLEAN NOT NULL,
    category VARCHAR(100),
    text TEXT NOT NULL,
    source VARCHAR(20) DEFAULT 'MANUAL',
    confidence NUMERIC(5,2),
    generated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fact_documents (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL REFERENCES dim_company(symbol),
    fiscal_year INT,
    annual_report TEXT,
    UNIQUE(symbol, fiscal_year, annual_report)
);
