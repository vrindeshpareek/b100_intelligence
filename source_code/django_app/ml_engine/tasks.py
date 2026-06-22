import subprocess
import sys
from pathlib import Path
from statistics import mean, pstdev

from celery import shared_task


@shared_task
def refresh_health_scores():
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, str(root / "etl" / "04_ml_scoring.py")],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=1800,
    )
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout[-2000:]


@shared_task
def detect_anomalies():
    from companies.models import FactProfitLoss
    from ml_engine.models import AnomalyFlag

    metrics = ("sales", "net_profit", "opm_pct")
    rows = list(
        FactProfitLoss.objects.filter(year__is_ttm=False)
        .select_related("year")
        .values("symbol_id", "year__fiscal_year", *metrics)
    )
    flags = []
    for metric in metrics:
        values = [float(row[metric]) for row in rows if row[metric] is not None]
        deviation = pstdev(values) if len(values) > 1 else 0
        if not deviation:
            continue
        average = mean(values)
        for row in rows:
            if row[metric] is None:
                continue
            z_score = (float(row[metric]) - average) / deviation
            if abs(z_score) >= 3:
                flags.append(
                    AnomalyFlag(
                        symbol=row["symbol_id"],
                        metric=metric,
                        fiscal_year=row["year__fiscal_year"],
                        method="Z_SCORE",
                        score=round(z_score, 4),
                        severity="HIGH" if abs(z_score) >= 4 else "MEDIUM",
                        details={"population_mean": average, "threshold": 3},
                    )
                )
    AnomalyFlag.objects.filter(method="Z_SCORE").delete()
    AnomalyFlag.objects.bulk_create(flags)
    return {"status": "complete", "flags_created": len(flags)}
