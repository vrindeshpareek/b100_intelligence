from django.db import models


class AnomalyFlag(models.Model):
    symbol = models.CharField(max_length=20, db_index=True)
    metric = models.CharField(max_length=100)
    fiscal_year = models.IntegerField(blank=True, null=True)
    method = models.CharField(max_length=30)
    score = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    severity = models.CharField(max_length=20, default="MEDIUM")
    details = models.JSONField(default=dict)
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ml_anomaly_flags"
        indexes = [models.Index(fields=["symbol", "detected_at"])]
