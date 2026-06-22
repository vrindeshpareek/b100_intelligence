import argparse
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from etl.utils import (
    CONFIG_DIR,
    DATA_CLEAN,
    banner,
    clean_scalar,
    get_engine,
    get_logger,
    test_db_connection,
)

logger = get_logger("03_load")

DROP_SQL = """
DROP TABLE IF EXISTS fact_documents, fact_pros_cons, fact_ml_scores, fact_analysis,
fact_cash_flow, fact_balance_sheet, fact_profit_loss,
dim_health_label, dim_year, dim_company, dim_sector CASCADE;
"""


def read_clean(name: str) -> pd.DataFrame:
    df = pd.read_csv(DATA_CLEAN / f"{name}.csv", encoding="utf-8-sig")
    df.columns = [c.lower() for c in df.columns]
    return df


def run_schema(conn, drop_first: bool) -> None:
    if drop_first:
        logger.warning("Dropping warehouse tables before reload")
        conn.execute(text(DROP_SQL))
    schema = (CONFIG_DIR / "schema.sql").read_text(encoding="utf-8")
    for statement in schema.split(";"):
        statement = statement.strip()
        if statement:
            conn.execute(text(statement))


def load_health_labels(conn):
    rows = [
        ("EXCELLENT", 80, 100, "#22c55e"),
        ("GOOD", 60, 80, "#86efac"),
        ("AVERAGE", 40, 60, "#fbbf24"),
        ("WEAK", 20, 40, "#f97316"),
        ("POOR", 0, 20, "#ef4444"),
    ]
    for name, min_score, max_score, color in rows:
        conn.execute(
            text("""
            INSERT INTO dim_health_label(label_name, min_score, max_score, color_hex)
            VALUES(:name, :min_score, :max_score, :color)
            ON CONFLICT(label_name) DO UPDATE SET min_score=EXCLUDED.min_score, max_score=EXCLUDED.max_score, color_hex=EXCLUDED.color_hex
        """),
            {
                "name": name,
                "min_score": min_score,
                "max_score": max_score,
                "color": color,
            },
        )


def load_dimensions(conn) -> dict:
    companies = read_clean("companies")
    sectors = read_clean("sector_mapping")
    for _, row in sectors.drop_duplicates("sector").iterrows():
        sector = clean_scalar(row["sector"])
        conn.execute(
            text("""
            INSERT INTO dim_sector(sector_name, sector_code, description)
            VALUES(:name, :code, :description)
            ON CONFLICT(sector_name) DO UPDATE SET sector_code=EXCLUDED.sector_code, description=EXCLUDED.description
        """),
            {
                "name": sector,
                "code": str(sector).upper().replace(" ", "_")[:20],
                "description": f"{sector} sector",
            },
        )

    companies = companies.merge(sectors, on="symbol", how="left")
    for _, row in companies.iterrows():
        data = {
            key: clean_scalar(row.get(key))
            for key in [
                "symbol",
                "company_name",
                "sector",
                "sub_sector",
                "company_logo",
                "website",
                "nse_url",
                "bse_url",
                "face_value",
                "book_value",
                "about_company",
                "chart_link",
                "roce_pct",
                "roe_pct",
            ]
        }
        conn.execute(
            text("""
            INSERT INTO dim_company(symbol, company_name, sector, sub_sector, company_logo, website, nse_url, bse_url, face_value, book_value, about_company, chart_link, roce_pct, roe_pct)
            VALUES(:symbol, :company_name, :sector, :sub_sector, :company_logo, :website, :nse_url, :bse_url, :face_value, :book_value, :about_company, :chart_link, :roce_pct, :roe_pct)
            ON CONFLICT(symbol) DO UPDATE SET
                company_name=EXCLUDED.company_name, sector=EXCLUDED.sector, sub_sector=EXCLUDED.sub_sector,
                company_logo=EXCLUDED.company_logo, website=EXCLUDED.website, nse_url=EXCLUDED.nse_url,
                bse_url=EXCLUDED.bse_url, face_value=EXCLUDED.face_value, book_value=EXCLUDED.book_value,
                about_company=EXCLUDED.about_company, chart_link=EXCLUDED.chart_link, roce_pct=EXCLUDED.roce_pct, roe_pct=EXCLUDED.roe_pct
        """),
            data,
        )

    year_frames = []
    for name in ["profitandloss", "balancesheet", "cashflow", "documents"]:
        df = read_clean(name)
        cols = [
            "year_label",
            "fiscal_year",
            "quarter",
            "is_ttm",
            "is_half_year",
            "sort_order",
        ]
        year_frames.append(df[[col for col in cols if col in df.columns]])
    years = (
        pd.concat(year_frames)
        .dropna(subset=["year_label"])
        .drop_duplicates("year_label")
    )
    for _, row in years.iterrows():
        data = {
            key: clean_scalar(row.get(key))
            for key in [
                "year_label",
                "fiscal_year",
                "quarter",
                "is_ttm",
                "is_half_year",
                "sort_order",
            ]
        }
        conn.execute(
            text("""
            INSERT INTO dim_year(year_label, fiscal_year, quarter, is_ttm, is_half_year, sort_order)
            VALUES(:year_label, :fiscal_year, :quarter, :is_ttm, :is_half_year, :sort_order)
            ON CONFLICT(year_label) DO UPDATE SET fiscal_year=EXCLUDED.fiscal_year, quarter=EXCLUDED.quarter, is_ttm=EXCLUDED.is_ttm, is_half_year=EXCLUDED.is_half_year, sort_order=EXCLUDED.sort_order
        """),
            data,
        )
    load_health_labels(conn)
    logger.info("Dimensions loaded: %s companies, %s years", len(companies), len(years))
    return dict(
        conn.execute(text("SELECT year_label, year_id FROM dim_year")).fetchall()
    )


def valid_symbols(conn) -> set[str]:
    return {
        row[0]
        for row in conn.execute(text("SELECT symbol FROM dim_company")).fetchall()
    }


def load_fact_profit_loss(conn, year_ids, symbols):
    df = read_clean("profitandloss")
    cols = [
        "sales",
        "expenses",
        "operating_profit",
        "opm_pct",
        "other_income",
        "interest",
        "depreciation",
        "profit_before_tax",
        "tax_pct",
        "net_profit",
        "eps",
        "dividend_payout_pct",
        "net_profit_margin_pct",
        "expense_ratio_pct",
        "interest_coverage",
    ]
    count = 0
    for _, row in df.iterrows():
        symbol = str(row["symbol"]).upper()
        year_id = year_ids.get(row["year_label"])
        if symbol not in symbols or not year_id:
            continue
        data = {col: clean_scalar(row.get(col)) for col in cols}
        data.update({"symbol": symbol, "year_id": year_id})
        conn.execute(
            text("""
            INSERT INTO fact_profit_loss(symbol, year_id, sales, expenses, operating_profit, opm_pct, other_income, interest, depreciation, profit_before_tax, tax_pct, net_profit, eps, dividend_payout_pct, net_profit_margin_pct, expense_ratio_pct, interest_coverage)
            VALUES(:symbol, :year_id, :sales, :expenses, :operating_profit, :opm_pct, :other_income, :interest, :depreciation, :profit_before_tax, :tax_pct, :net_profit, :eps, :dividend_payout_pct, :net_profit_margin_pct, :expense_ratio_pct, :interest_coverage)
            ON CONFLICT(symbol, year_id) DO UPDATE SET sales=EXCLUDED.sales, expenses=EXCLUDED.expenses, operating_profit=EXCLUDED.operating_profit, opm_pct=EXCLUDED.opm_pct, other_income=EXCLUDED.other_income, interest=EXCLUDED.interest, depreciation=EXCLUDED.depreciation, profit_before_tax=EXCLUDED.profit_before_tax, tax_pct=EXCLUDED.tax_pct, net_profit=EXCLUDED.net_profit, eps=EXCLUDED.eps, dividend_payout_pct=EXCLUDED.dividend_payout_pct, net_profit_margin_pct=EXCLUDED.net_profit_margin_pct, expense_ratio_pct=EXCLUDED.expense_ratio_pct, interest_coverage=EXCLUDED.interest_coverage
        """),
            data,
        )
        count += 1
    logger.info("fact_profit_loss: %s", count)


def load_fact_balance_sheet(conn, year_ids, symbols):
    df = read_clean("balancesheet")
    cols = [
        "equity_capital",
        "reserves",
        "borrowings",
        "other_liabilities",
        "total_liabilities",
        "fixed_assets",
        "cwip",
        "investments",
        "other_assets",
        "total_assets",
        "debt_to_equity",
        "equity_ratio",
    ]
    count = 0
    for _, row in df.iterrows():
        symbol = str(row["symbol"]).upper()
        year_id = year_ids.get(row["year_label"])
        if symbol not in symbols or not year_id:
            continue
        data = {col: clean_scalar(row.get(col)) for col in cols}
        data.update({"symbol": symbol, "year_id": year_id})
        conn.execute(
            text("""
            INSERT INTO fact_balance_sheet(symbol, year_id, equity_capital, reserves, borrowings, other_liabilities, total_liabilities, fixed_assets, cwip, investments, other_assets, total_assets, debt_to_equity, equity_ratio)
            VALUES(:symbol, :year_id, :equity_capital, :reserves, :borrowings, :other_liabilities, :total_liabilities, :fixed_assets, :cwip, :investments, :other_assets, :total_assets, :debt_to_equity, :equity_ratio)
            ON CONFLICT(symbol, year_id) DO UPDATE SET equity_capital=EXCLUDED.equity_capital, reserves=EXCLUDED.reserves, borrowings=EXCLUDED.borrowings, other_liabilities=EXCLUDED.other_liabilities, total_liabilities=EXCLUDED.total_liabilities, fixed_assets=EXCLUDED.fixed_assets, cwip=EXCLUDED.cwip, investments=EXCLUDED.investments, other_assets=EXCLUDED.other_assets, total_assets=EXCLUDED.total_assets, debt_to_equity=EXCLUDED.debt_to_equity, equity_ratio=EXCLUDED.equity_ratio
        """),
            data,
        )
        count += 1
    logger.info("fact_balance_sheet: %s", count)


def load_fact_cash_flow(conn, year_ids, symbols):
    df = read_clean("cashflow")
    cols = [
        "operating_activity",
        "investing_activity",
        "financing_activity",
        "net_cash_flow",
        "free_cash_flow",
        "cash_conversion_ratio",
    ]
    count = 0
    for _, row in df.iterrows():
        symbol = str(row["symbol"]).upper()
        year_id = year_ids.get(row["year_label"])
        if symbol not in symbols or not year_id:
            continue
        data = {col: clean_scalar(row.get(col)) for col in cols}
        data.update({"symbol": symbol, "year_id": year_id})
        conn.execute(
            text("""
            INSERT INTO fact_cash_flow(symbol, year_id, operating_activity, investing_activity, financing_activity, net_cash_flow, free_cash_flow, cash_conversion_ratio)
            VALUES(:symbol, :year_id, :operating_activity, :investing_activity, :financing_activity, :net_cash_flow, :free_cash_flow, :cash_conversion_ratio)
            ON CONFLICT(symbol, year_id) DO UPDATE SET operating_activity=EXCLUDED.operating_activity, investing_activity=EXCLUDED.investing_activity, financing_activity=EXCLUDED.financing_activity, net_cash_flow=EXCLUDED.net_cash_flow, free_cash_flow=EXCLUDED.free_cash_flow, cash_conversion_ratio=EXCLUDED.cash_conversion_ratio
        """),
            data,
        )
        count += 1
    logger.info("fact_cash_flow: %s", count)


def load_fact_analysis(conn, symbols):
    df = read_clean("analysis")
    count = 0
    for _, row in df.iterrows():
        symbol = str(row["symbol"]).upper()
        if symbol not in symbols:
            continue
        data = {
            col: clean_scalar(row.get(col))
            for col in [
                "period_label",
                "compounded_sales_growth_pct",
                "compounded_profit_growth_pct",
                "stock_price_cagr_pct",
                "roe_pct",
            ]
        }
        data["symbol"] = symbol
        conn.execute(
            text("""
            INSERT INTO fact_analysis(symbol, period_label, compounded_sales_growth_pct, compounded_profit_growth_pct, stock_price_cagr_pct, roe_pct)
            VALUES(:symbol, :period_label, :compounded_sales_growth_pct, :compounded_profit_growth_pct, :stock_price_cagr_pct, :roe_pct)
            ON CONFLICT(symbol, period_label) DO UPDATE SET compounded_sales_growth_pct=EXCLUDED.compounded_sales_growth_pct, compounded_profit_growth_pct=EXCLUDED.compounded_profit_growth_pct, stock_price_cagr_pct=EXCLUDED.stock_price_cagr_pct, roe_pct=EXCLUDED.roe_pct
        """),
            data,
        )
        count += 1
    logger.info("fact_analysis: %s", count)


def load_fact_pros_cons(conn, symbols):
    df = read_clean("prosandcons")
    conn.execute(text("DELETE FROM fact_pros_cons WHERE source = 'MANUAL'"))
    count = 0
    for _, row in df.iterrows():
        symbol = str(row["symbol"]).upper()
        if symbol not in symbols:
            continue
        conn.execute(
            text("""
            INSERT INTO fact_pros_cons(symbol, is_pro, category, text, source, confidence, generated_at)
            VALUES(:symbol, :is_pro, :category, :text, :source, :confidence, :generated_at)
        """),
            {
                col: clean_scalar(row.get(col))
                for col in [
                    "symbol",
                    "is_pro",
                    "category",
                    "text",
                    "source",
                    "confidence",
                    "generated_at",
                ]
            },
        )
        count += 1
    logger.info("fact_pros_cons: %s", count)


def load_fact_documents(conn, symbols):
    df = read_clean("documents")
    count = 0
    for _, row in df.iterrows():
        symbol = str(row["symbol"]).upper()
        if symbol not in symbols:
            continue
        conn.execute(
            text("""
            INSERT INTO fact_documents(symbol, fiscal_year, annual_report)
            VALUES(:symbol, :fiscal_year, :annual_report)
            ON CONFLICT(symbol, fiscal_year, annual_report) DO NOTHING
        """),
            {
                "symbol": symbol,
                "fiscal_year": clean_scalar(row.get("fiscal_year")),
                "annual_report": clean_scalar(row.get("annual_report")),
            },
        )
        count += 1
    logger.info("fact_documents: %s", count)


def update_cross_metrics(conn):
    conn.execute(text("""
        UPDATE fact_cash_flow cf
        SET cash_conversion_ratio = cf.operating_activity / NULLIF(pl.net_profit, 0)
        FROM fact_profit_loss pl
        WHERE cf.symbol = pl.symbol AND cf.year_id = pl.year_id
    """))
    conn.execute(text("""
        UPDATE fact_profit_loss pl
        SET asset_turnover = pl.sales / NULLIF(bs.total_assets, 0),
            return_on_assets = (pl.net_profit / NULLIF(bs.total_assets, 0)) * 100
        FROM fact_balance_sheet bs
        WHERE pl.symbol = bs.symbol AND pl.year_id = bs.year_id
    """))


def dq(conn):
    for table in [
        "dim_company",
        "dim_year",
        "dim_sector",
        "fact_profit_loss",
        "fact_balance_sheet",
        "fact_cash_flow",
        "fact_analysis",
        "fact_pros_cons",
        "fact_documents",
        "fact_ml_scores",
    ]:
        # Table names come only from the static allow-list above.
        logger.info(
            "%-22s %s",
            table,
            conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar(),  # nosec B608
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--drop-first", action="store_true")
    args = parser.parse_args()
    banner("STEP 03 - Load Warehouse")
    engine = get_engine()
    if not test_db_connection(engine, logger):
        sys.exit(1)
    with engine.begin() as conn:
        run_schema(conn, args.drop_first)
        year_ids = load_dimensions(conn)
        symbols = valid_symbols(conn)
        load_fact_profit_loss(conn, year_ids, symbols)
        load_fact_balance_sheet(conn, year_ids, symbols)
        load_fact_cash_flow(conn, year_ids, symbols)
        load_fact_analysis(conn, symbols)
        load_fact_pros_cons(conn, symbols)
        load_fact_documents(conn, symbols)
        update_cross_metrics(conn)
        dq(conn)


if __name__ == "__main__":
    main()
