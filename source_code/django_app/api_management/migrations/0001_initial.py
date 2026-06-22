import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="ChannelPartner",
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
                ("name", models.CharField(max_length=200)),
                ("contact_email", models.EmailField(max_length=254)),
                (
                    "tier",
                    models.CharField(
                        choices=[
                            ("BASIC", "Basic"),
                            ("PRO", "Pro"),
                            ("ENTERPRISE", "Enterprise"),
                        ],
                        default="BASIC",
                        max_length=20,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="APIKey",
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
                (
                    "key_id",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("name", models.CharField(max_length=100)),
                ("secret_hash", models.CharField(max_length=200)),
                ("encrypted_secret", models.TextField()),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                (
                    "partner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="api_keys",
                        to="api_management.channelpartner",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="WebhookEndpoint",
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
                ("url", models.URLField()),
                (
                    "event",
                    models.CharField(
                        choices=[
                            ("score_updated", "Score updated"),
                            ("anomaly_flagged", "Anomaly flagged"),
                        ],
                        max_length=40,
                    ),
                ),
                ("secret_hash", models.CharField(max_length=200)),
                ("encrypted_secret", models.TextField()),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "partner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="webhooks",
                        to="api_management.channelpartner",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="APIUsageLog",
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
                ("method", models.CharField(max_length=10)),
                ("path", models.CharField(max_length=500)),
                ("status_code", models.PositiveSmallIntegerField()),
                ("response_ms", models.PositiveIntegerField(default=0)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "api_key",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="api_management.apikey",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="apiusagelog",
            index=models.Index(
                fields=["api_key", "created_at"], name="api_managem_api_key_9039e5_idx"
            ),
        ),
    ]
