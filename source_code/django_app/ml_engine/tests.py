from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from .tasks import detect_anomalies, refresh_health_scores


class MlTaskTests(SimpleTestCase):
    @patch("ml_engine.tasks.subprocess.run")
    def test_refresh_health_scores_runs_pipeline(self, run):
        run.return_value = SimpleNamespace(
            returncode=0, stdout="scores refreshed", stderr=""
        )
        self.assertEqual(refresh_health_scores.run(), "scores refreshed")
        self.assertIn("04_ml_scoring.py", run.call_args.args[0][1])

    @patch("ml_engine.tasks.subprocess.run")
    def test_refresh_health_scores_reports_pipeline_failure(self, run):
        run.return_value = SimpleNamespace(
            returncode=1, stdout="", stderr="database error"
        )
        with self.assertRaisesRegex(RuntimeError, "database error"):
            refresh_health_scores.run()

    @patch("ml_engine.models.AnomalyFlag.objects")
    @patch("companies.models.FactProfitLoss.objects")
    def test_detect_anomalies_replaces_z_score_flags(
        self, profit_objects, flag_objects
    ):
        rows = [
            {
                "symbol_id": f"C{index}",
                "year__fiscal_year": 2025,
                "sales": 0,
                "net_profit": 10,
                "opm_pct": None,
            }
            for index in range(10)
        ]
        rows.append(
            {
                "symbol_id": "OUTLIER",
                "year__fiscal_year": 2025,
                "sales": 100,
                "net_profit": 10,
                "opm_pct": None,
            }
        )
        values = profit_objects.filter.return_value.select_related.return_value.values
        values.return_value = rows

        result = detect_anomalies.run()

        self.assertEqual(result, {"status": "complete", "flags_created": 1})
        flag_objects.filter.assert_called_once_with(method="Z_SCORE")
        flag_objects.filter.return_value.delete.assert_called_once_with()
        created = flag_objects.bulk_create.call_args.args[0]
        self.assertEqual(created[0].symbol, "OUTLIER")
        self.assertEqual(created[0].metric, "sales")
