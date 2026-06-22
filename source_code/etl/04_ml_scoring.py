import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from etl.utils import (
    DATA_WH,
    banner,
    clean_scalar,
    get_engine,
    get_logger,
    test_db_connection,
)

logger = get_logger("04_ml_scoring")

WEIGHTS = {
    "profitability": 0.30,
    "growth": 0.25,
    "leverage": 0.20,
    "cashflow": 0.15,
    "dividend": 0.05,
    "trend": 0.05,
}


def score(series, higher=True):
    s = pd.to_numeric(series, errors="coerce")
    valid = s.dropna()
    if len(valid) < 2 or valid.max() == valid.min():
        return pd.Series(50.0, index=s.index)
    out = (s - valid.min()) / (valid.max() - valid.min()) * 100
    out = out.fillna(50).clip(0, 100)
    return out if higher else 100 - out


def label(value):
    if value >= 80:
        return "EXCELLENT"
    if value >= 60:
        return "GOOD"
    if value >= 40:
        return "AVERAGE"
    if value >= 20:
        return "WEAK"
    return "POOR"


def load_tables(engine):
    with engine.connect() as conn:
        # Names are fixed source-code constants, never user input.
        return {
            name: pd.read_sql(f"SELECT * FROM {name}", conn)  # nosec B608
            for name in [
                "dim_company",
                "dim_year",
                "fact_profit_loss",
                "fact_balance_sheet",
                "fact_cash_flow",
                "fact_analysis",
            ]
        }  # nosec B608


def compute(tables):
    companies = tables["dim_company"]["symbol"].tolist()
    pl = tables["fact_profit_loss"].merge(
        tables["dim_year"][["year_id", "sort_order"]], on="year_id", how="left"
    )
    bs = tables["fact_balance_sheet"]
    cf = tables["fact_cash_flow"]
    an = tables["fact_analysis"]

    profitability = (
        score(pl.groupby("symbol")["net_profit_margin_pct"].mean()) * 0.45
        + score(pl.groupby("symbol")["opm_pct"].mean()) * 0.35
        + score(pl.groupby("symbol")["interest_coverage"].median().clip(upper=25))
        * 0.20
    )
    leverage = score(
        bs.groupby("symbol")["debt_to_equity"].mean().clip(lower=0, upper=10),
        higher=False,
    )
    cashflow = score(cf.groupby("symbol")["free_cash_flow"].mean())
    dividend = score(pl.groupby("symbol")["dividend_payout_pct"].mean().clip(0, 100))

    if an.empty:
        growth = pd.Series(50.0, index=companies)
    else:
        growth = score(an.groupby("symbol")["compounded_sales_growth_pct"].mean())

    def trend_for(group):
        g = group.sort_values("sort_order").tail(5)
        if len(g) < 2:
            return 0.0
        return float(
            np.polyfit(range(len(g)), g["net_profit_margin_pct"].fillna(0), 1)[0]
        )

    trend = score(pl.groupby("symbol").apply(trend_for))

    rows = []
    now = datetime.now()
    for symbol in companies:
        row = {
            "symbol": symbol,
            "profitability_score": round(float(profitability.get(symbol, 50)), 2),
            "growth_score": round(float(growth.get(symbol, 50)), 2),
            "leverage_score": round(float(leverage.get(symbol, 50)), 2),
            "cashflow_score": round(float(cashflow.get(symbol, 50)), 2),
            "dividend_score": round(float(dividend.get(symbol, 50)), 2),
            "trend_score": round(float(trend.get(symbol, 50)), 2),
        }
        overall = sum(row[f"{name}_score"] * weight for name, weight in WEIGHTS.items())
        row["overall_score"] = round(overall, 2)
        row["health_label"] = label(overall)
        row["computed_at"] = now
        rows.append(row)
    return pd.DataFrame(rows)


def save(engine, df):
    DATA_WH.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_WH / "ml_scores.csv", index=False, encoding="utf-8-sig")
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM fact_ml_scores"))
        for _, row in df.iterrows():
            data = {col: clean_scalar(row.get(col)) for col in df.columns}
            conn.execute(
                text("""
                INSERT INTO fact_ml_scores(symbol, computed_at, overall_score, profitability_score, growth_score, leverage_score, cashflow_score, dividend_score, trend_score, health_label)
                VALUES(:symbol, :computed_at, :overall_score, :profitability_score, :growth_score, :leverage_score, :cashflow_score, :dividend_score, :trend_score, :health_label)
            """),
                data,
            )


def main():
    banner("STEP 04 - ML Health Scoring")
    engine = get_engine()
    if not test_db_connection(engine, logger):
        sys.exit(1)
    df = compute(load_tables(engine))
    save(engine, df)
    logger.info("ML scores loaded: %s companies", len(df))


if __name__ == "__main__":
    main()
