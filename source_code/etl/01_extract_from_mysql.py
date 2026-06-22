import argparse
import re
import sys
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from etl.utils import DATA_RAW, banner, get_logger, normalize_columns

logger = get_logger("01_extract")

TABLES = [
    "companies",
    "analysis",
    "balancesheet",
    "profitandloss",
    "cashflow",
    "prosandcons",
    "documents",
]


def promote_export_header(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(how="all").copy()
    header_idx = 0
    for idx, row in df.head(10).iterrows():
        values = {str(v).strip().lower() for v in row.tolist() if pd.notna(v)}
        if "id" in values or "company_id" in values:
            header_idx = idx
            break
    out = df.iloc[header_idx + 1 :].copy()
    out.columns = normalize_columns(df.iloc[header_idx].tolist())
    out = out.dropna(how="all").replace(
        {"NULL": np.nan, "Null": np.nan, "null": np.nan, "": np.nan}
    )
    return out.reset_index(drop=True)


def extract_excel(raw_dir: Path) -> dict[str, pd.DataFrame]:
    found = {}
    for path in sorted(list(raw_dir.glob("*.xlsx")) + list(raw_dir.glob("*.xls"))):
        table = path.stem.lower().replace(" ", "_").replace("-", "_")
        if table in TABLES:
            try:
                df = pd.read_excel(path, header=None, dtype=str)
            except ImportError as exc:
                logger.warning("Cannot read Excel files yet: %s", exc)
                return {}
            found[table] = promote_export_header(df)
            logger.info(
                "%s: %s rows, %s cols",
                table,
                len(found[table]),
                len(found[table].columns),
            )
    if found:
        return found

    for path in sorted(list(raw_dir.glob("*.xlsx")) + list(raw_dir.glob("*.xls"))):
        try:
            book = pd.ExcelFile(path)
        except ImportError as exc:
            logger.warning("Cannot read Excel files yet: %s", exc)
            return {}
        for sheet in book.sheet_names:
            sheet_key = sheet.lower().replace(" ", "_").replace("-", "_")
            match = next(
                (table for table in TABLES if table in sheet_key or sheet_key in table),
                None,
            )
            if match:
                found[match] = promote_export_header(
                    book.parse(sheet, header=None, dtype=str)
                )
                logger.info(
                    "%s: %s rows, %s cols",
                    match,
                    len(found[match]),
                    len(found[match].columns),
                )
    return found


def extract_existing_csv(raw_dir: Path) -> dict[str, pd.DataFrame]:
    found = {}
    for table in TABLES:
        path = raw_dir / f"{table}.csv"
        if path.exists():
            df = pd.read_csv(path, header=None, dtype=str, encoding="utf-8-sig")
            found[table] = promote_export_header(df)
            logger.info(
                "%s: %s rows, %s cols",
                table,
                len(found[table]),
                len(found[table].columns),
            )
    return found


def split_sql_values(row: str) -> list:
    reader = pd.read_csv(
        StringIO(row),
        header=None,
        quotechar="'",
        escapechar="\\",
        keep_default_na=False,
    )
    return reader.iloc[0].replace({"NULL": None, "null": None}).tolist()


def extract_sql(path: Path) -> dict[str, pd.DataFrame]:
    text = path.read_text(encoding="utf-8", errors="replace")
    schema = {}
    for table, body in re.findall(
        r"CREATE TABLE\s+`?(\w+)`?\s*\((.*?)\)\s*ENGINE", text, flags=re.I | re.S
    ):
        cols = re.findall(r"^\s*`([^`]+)`", body, flags=re.M)
        schema[table.lower()] = cols

    rows = {table: [] for table in TABLES}
    pattern = re.compile(
        r"INSERT INTO\s+`?(\w+)`?\s*(?:\([^)]+\))?\s*VALUES\s*(.*?);", re.I | re.S
    )
    for table, values in pattern.findall(text):
        table = table.lower()
        if table not in rows:
            continue
        chunks = re.findall(r"\((.*?)\)(?:,|$)", values, flags=re.S)
        for chunk in chunks:
            rows[table].append(split_sql_values(chunk))

    out = {}
    for table, table_rows in rows.items():
        if not table_rows:
            continue
        cols = schema.get(table) or [
            f"col_{i}" for i in range(max(len(row) for row in table_rows))
        ]
        out[table] = pd.DataFrame(table_rows, columns=normalize_columns(cols))
        logger.info(
            "%s: %s rows, %s cols", table, len(out[table]), len(out[table].columns)
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source", choices=["auto", "excel", "csv", "sql"], default="auto"
    )
    parser.add_argument("--file", type=Path)
    args = parser.parse_args()
    banner("STEP 01 - Extract Raw Data")

    if args.source == "sql" or (args.source == "auto" and list(DATA_RAW.glob("*.sql"))):
        sql_path = args.file or next(DATA_RAW.glob("*.sql"))
        frames = extract_sql(sql_path)
    elif args.source == "csv":
        frames = extract_existing_csv(DATA_RAW)
    else:
        frames = extract_excel(DATA_RAW)
        if not frames and args.source == "auto":
            frames = extract_existing_csv(DATA_RAW)

    missing = [table for table in TABLES if table not in frames]
    if missing:
        logger.warning("Missing tables: %s", missing)

    for table, df in frames.items():
        df.to_csv(DATA_RAW / f"{table}.csv", index=False, encoding="utf-8-sig")
        logger.info("Saved data/raw/%s.csv", table)


if __name__ == "__main__":
    main()
