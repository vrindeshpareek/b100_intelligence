import logging
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_CLEAN = PROJECT_ROOT / "data" / "clean"
DATA_WH = PROJECT_ROOT / "data" / "warehouse"
LOGS_DIR = PROJECT_ROOT / "logs"

for folder in [CONFIG_DIR, DATA_RAW, DATA_CLEAN, DATA_WH, LOGS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)


def load_env() -> None:
    env_path = CONFIG_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_db_url() -> str:
    load_env()
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "bluestock_dw")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "b100pass")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"


def get_engine(echo: bool = False):
    return create_engine(get_db_url(), echo=echo, future=True)


def test_db_connection(engine, logger) -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection OK")
        return True
    except Exception as exc:
        logger.error("Database connection failed: %s", exc)
        return False


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s - %(message)s", "%H:%M:%S"
    )
    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(formatter)
    logger.addHandler(stream)
    file_handler = logging.FileHandler(LOGS_DIR / f"{name}.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def banner(title: str) -> None:
    print("\n" + "=" * 72)
    print(f"  {title}")
    print("=" * 72)


def normalize_columns(columns) -> list[str]:
    return [
        str(col).strip().lower().replace(" ", "_").replace("&", "and")
        for col in columns
    ]


def clean_scalar(value):
    try:
        import pandas as pd

        if pd.isna(value):
            return None
    except Exception:
        pass
    if isinstance(value, str):
        value = value.strip()
        if value == "" or value.lower() in {"nan", "none", "null"}:
            return None
    return value
