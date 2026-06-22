import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from etl.utils import DATA_CLEAN, DATA_RAW, banner, get_logger

logger = get_logger("02_clean")

MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

SECTOR_MAP = {
    "TCS": ("IT", "Large Cap IT"),
    "INFY": ("IT", "Large Cap IT"),
    "WIPRO": ("IT", "Large Cap IT"),
    "HCLTECH": ("IT", "Large Cap IT"),
    "HDFCBANK": ("Banking", "Private Bank"),
    "ICICIBANK": ("Banking", "Private Bank"),
    "AXISBANK": ("Banking", "Private Bank"),
    "KOTAKBANK": ("Banking", "Private Bank"),
    "SBIN": ("Banking", "PSU Bank"),
    "BANKBARODA": ("Banking", "PSU Bank"),
    "CANBK": ("Banking", "PSU Bank"),
    "PNB": ("Banking", "PSU Bank"),
    "BAJFINANCE": ("NBFC", "Consumer Finance"),
    "BAJAJFINSV": ("NBFC", "Diversified Finance"),
    "SBILIFE": ("Insurance", "Life Insurance"),
    "HDFCLIFE": ("Insurance", "Life Insurance"),
    "RELIANCE": ("Energy", "Integrated Energy"),
    "ONGC": ("Energy", "Oil & Gas"),
    "IOC": ("Energy", "Oil Marketing"),
    "BPCL": ("Energy", "Oil Marketing"),
    "ADANIGREEN": ("Power", "Renewable Energy"),
    "ADANIPOWER": ("Power", "Thermal Power"),
    "ADANIENSOL": ("Power", "Transmission"),
    "NTPC": ("Power", "Thermal Power"),
    "POWERGRID": ("Power", "Transmission"),
    "ADANIPORTS": ("Ports", "Ports & Logistics"),
    "ADANIENT": ("Holding Company", "Diversified Holding"),
    "ULTRACEMCO": ("Cement", "Large Cap Cement"),
    "AMBUJACEM": ("Cement", "Large Cap Cement"),
    "ACC": ("Cement", "Large Cap Cement"),
    "APOLLOHOSP": ("Healthcare", "Hospital"),
    "SUNPHARMA": ("Pharma", "Large Cap Pharma"),
    "DRREDDY": ("Pharma", "Large Cap Pharma"),
    "CIPLA": ("Pharma", "Large Cap Pharma"),
    "HINDUNILVR": ("Consumer Goods", "FMCG"),
    "ITC": ("Consumer Goods", "Diversified FMCG"),
    "NESTLEIND": ("Consumer Goods", "FMCG"),
    "BRITANNIA": ("Consumer Goods", "FMCG"),
    "ASIANPAINT": ("Paints", "Decorative Paints"),
    "BAJAJ-AUTO": ("Auto", "2-Wheeler"),
    "MARUTI": ("Auto", "Passenger Vehicles"),
    "TATAMOTORS": ("Auto", "Auto"),
    "BHARTIARTL": ("Telecom", "Telecom"),
    "TATASTEEL": ("Metals", "Steel"),
    "JSWSTEEL": ("Metals", "Steel"),
    "HINDALCO": ("Metals", "Aluminium"),
    "LT": ("Infrastructure", "Engineering"),
    "DMART": ("Retail", "Retail"),
    "TRENT": ("Retail", "Retail"),
}


def read_raw(name: str) -> pd.DataFrame:
    df = pd.read_csv(DATA_RAW / f"{name}.csv", dtype=str, encoding="utf-8-sig")
    df.columns = [
        str(c).strip().lower().replace(" ", "_").replace("&", "and") for c in df.columns
    ]
    return df.replace({"NULL": np.nan, "Null": np.nan, "null": np.nan, "": np.nan})


def num(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.strip(),
        errors="coerce",
    )


def div(a, b):
    return a.div(b.replace(0, np.nan))


def parse_year(value) -> dict:
    if pd.isna(value) or str(value).strip() == "":
        return {
            "year_label": None,
            "fiscal_year": None,
            "quarter": None,
            "is_ttm": False,
            "is_half_year": False,
            "sort_order": None,
        }
    s = str(value).strip()
    if s.upper() == "TTM":
        return {
            "year_label": "TTM",
            "fiscal_year": None,
            "quarter": None,
            "is_ttm": True,
            "is_half_year": False,
            "sort_order": 999999,
        }
    if re.fullmatch(r"\d{4}\.5", s):
        year = int(float(s))
        return {
            "year_label": f"Sep {year}",
            "fiscal_year": year,
            "quarter": "Q2",
            "is_ttm": False,
            "is_half_year": True,
            "sort_order": year * 100 + 9,
        }
    match = re.match(r"([A-Za-z]{3})[\s-]?(\d{2,4})$", s)
    if match:
        mon = match.group(1).lower()
        year = int(match.group(2))
        if year < 100:
            year += 2000 if year <= 30 else 1900
        month = MONTHS.get(mon, 3)
        qtr = (
            "Q4"
            if month in [1, 2, 3]
            else "Q1" if month in [4, 5, 6] else "Q2" if month in [7, 8, 9] else "Q3"
        )
        return {
            "year_label": f"{mon.title()} {year}",
            "fiscal_year": year,
            "quarter": qtr,
            "is_ttm": False,
            "is_half_year": False,
            "sort_order": year * 100 + month,
        }
    if re.fullmatch(r"\d{4}", s):
        year = int(s)
        return {
            "year_label": f"Mar {year}",
            "fiscal_year": year,
            "quarter": "Q4",
            "is_ttm": False,
            "is_half_year": False,
            "sort_order": year * 100 + 3,
        }
    return {
        "year_label": s,
        "fiscal_year": None,
        "quarter": None,
        "is_ttm": False,
        "is_half_year": False,
        "sort_order": 0,
    }


def add_years(df: pd.DataFrame, column: str) -> pd.DataFrame:
    parsed = df[column].apply(parse_year).apply(pd.Series)
    return pd.concat([df, parsed], axis=1)


def clean_companies() -> pd.DataFrame:
    df = read_raw("companies").rename(
        columns={
            "id": "symbol",
            "nse_profile": "nse_url",
            "bse_profile": "bse_url",
            "roce_percentage": "roce_pct",
            "roe_percentage": "roe_pct",
        }
    )
    df["symbol"] = df["symbol"].astype(str).str.upper().str.strip()
    df["company_name"] = (
        df["company_name"]
        .astype(str)
        .str.replace(r"[\r\n]+", " ", regex=True)
        .str.strip()
    )
    for col in ["face_value", "book_value", "roce_pct", "roe_pct"]:
        if col in df:
            df[col] = num(df[col])
    return df


def clean_balancesheet() -> pd.DataFrame:
    df = add_years(read_raw("balancesheet"), "year").rename(
        columns={"company_id": "symbol", "other_asset": "other_assets"}
    )
    df["symbol"] = df["symbol"].astype(str).str.upper().str.strip()
    for col in [
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
    ]:
        df[col] = num(df[col])
    equity = df["equity_capital"].fillna(0) + df["reserves"].fillna(0)
    df["debt_to_equity"] = div(df["borrowings"], equity)
    df["equity_ratio"] = div(equity, df["total_assets"]) * 100
    return df


def clean_profitloss() -> pd.DataFrame:
    df = add_years(read_raw("profitandloss"), "year").rename(
        columns={
            "company_id": "symbol",
            "opm_percentage": "opm_pct",
            "tax_percentage": "tax_pct",
            "dividend_payout": "dividend_payout_pct",
        }
    )
    df["symbol"] = df["symbol"].astype(str).str.upper().str.strip()
    for col in [
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
    ]:
        df[col] = num(df[col])
    df["net_profit_margin_pct"] = div(df["net_profit"], df["sales"]) * 100
    df["expense_ratio_pct"] = div(df["expenses"], df["sales"]) * 100
    df["interest_coverage"] = div(df["operating_profit"], df["interest"])
    return df


def clean_cashflow() -> pd.DataFrame:
    df = add_years(read_raw("cashflow"), "year").rename(
        columns={"company_id": "symbol"}
    )
    df["symbol"] = df["symbol"].astype(str).str.upper().str.strip()
    for col in [
        "operating_activity",
        "investing_activity",
        "financing_activity",
        "net_cash_flow",
    ]:
        df[col] = num(df[col])
    df["free_cash_flow"] = df["operating_activity"].fillna(0) + df[
        "investing_activity"
    ].fillna(0)
    df["cash_conversion_ratio"] = np.nan
    return df


def pct_from_text(value):
    match = re.search(r"(-?\d+(?:\.\d+)?)\s*%?", str(value))
    return float(match.group(1)) if match else np.nan


def period_from_text(value):
    s = str(value)
    match = re.search(r"(\d+)\s*Years?", s, flags=re.I)
    if match:
        return f"{match.group(1)}Y"
    if "TTM" in s.upper() or "1 YEAR" in s.upper() or "LAST YEAR" in s.upper():
        return "TTM"
    return None


def clean_analysis() -> pd.DataFrame:
    df = read_raw("analysis").rename(columns={"company_id": "symbol"})
    rows = []
    for _, row in df.iterrows():
        period = period_from_text(row.get("compounded_sales_growth"))
        if not period:
            continue
        rows.append(
            {
                "symbol": str(row["symbol"]).upper().strip(),
                "period_label": period,
                "compounded_sales_growth_pct": pct_from_text(
                    row.get("compounded_sales_growth")
                ),
                "compounded_profit_growth_pct": pct_from_text(
                    row.get("compounded_profit_growth")
                ),
                "stock_price_cagr_pct": pct_from_text(row.get("stock_price_cagr")),
                "roe_pct": pct_from_text(row.get("roe")),
            }
        )
    return pd.DataFrame(rows)


def clean_proscons() -> pd.DataFrame:
    df = read_raw("prosandcons").rename(columns={"company_id": "symbol"})
    rows = []
    for _, row in df.iterrows():
        sym = str(row["symbol"]).upper().strip()
        for is_pro, col in [(True, "pros"), (False, "cons")]:
            text = str(row.get(col, "")).strip()
            if text and text.lower() != "nan":
                rows.append(
                    {
                        "symbol": sym,
                        "is_pro": is_pro,
                        "category": "Manual",
                        "text": text,
                        "source": "MANUAL",
                        "confidence": 1.0,
                        "generated_at": pd.Timestamp.now().isoformat(),
                    }
                )
    return pd.DataFrame(rows)


def clean_documents() -> pd.DataFrame:
    df = add_years(
        read_raw("documents").rename(
            columns={"company_id": "symbol", "annual_report": "annual_report"}
        ),
        "year",
    )
    df["symbol"] = df["symbol"].astype(str).str.upper().str.strip()
    return df


def sector_mapping(companies: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sym in (
        companies["symbol"].dropna().astype(str).str.upper().str.strip().unique()
    ):
        sector, sub_sector = SECTOR_MAP.get(sym, ("Other", "Other"))
        rows.append({"symbol": sym, "sector": sector, "sub_sector": sub_sector})
    return pd.DataFrame(rows)


def main() -> None:
    banner("STEP 02 - Clean and Transform")
    cleaners = {
        "companies": clean_companies,
        "balancesheet": clean_balancesheet,
        "profitandloss": clean_profitloss,
        "cashflow": clean_cashflow,
        "analysis": clean_analysis,
        "prosandcons": clean_proscons,
        "documents": clean_documents,
    }
    outputs = {}
    for name, func in cleaners.items():
        outputs[name] = func()
        outputs[name].to_csv(
            DATA_CLEAN / f"{name}.csv", index=False, encoding="utf-8-sig"
        )
        logger.info(
            "%s: %s rows, %s cols", name, len(outputs[name]), len(outputs[name].columns)
        )
    sectors = sector_mapping(outputs["companies"])
    sectors.to_csv(DATA_CLEAN / "sector_mapping.csv", index=False, encoding="utf-8-sig")
    logger.info("sector_mapping: %s rows", len(sectors))


if __name__ == "__main__":
    main()
