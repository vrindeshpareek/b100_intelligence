from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="AnomalyFlag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("metric", models.CharField(max_length=100)),
                ("fiscal_year", models.IntegerField(blank=True, null=True)),
                ("method", models.CharField(max_length=30)),
                (
                    "score",
                    models.DecimalField(
                        blank=True, decimal_places=4, max_digits=12, null=True
                    ),
                ),
                ("severity", models.CharField(default="MEDIUM", max_length=20)),
                ("details", models.JSONField(default=dict)),
                ("detected_at", models.DateTimeField(auto_now_add=True)),
                ("symbol", models.CharField(db_index=True, max_length=20)),
            ],
            options={"db_table": "ml_anomaly_flags"},
        ),
        migrations.AddIndex(
            model_name="anomalyflag",
            index=models.Index(
                fields=["symbol", "detected_at"], name="ml_anomaly__symbol_1e7852_idx"
            ),
        ),
    ]
