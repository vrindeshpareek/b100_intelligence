import uuid

from django.db import models


class ChannelPartner(models.Model):
    TIERS = [("BASIC", "Basic"), ("PRO", "Pro"), ("ENTERPRISE", "Enterprise")]
    name = models.CharField(max_length=200)
    contact_email = models.EmailField()
    tier = models.CharField(max_length=20, choices=TIERS, default="BASIC")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class APIKey(models.Model):
    partner = models.ForeignKey(
        ChannelPartner, on_delete=models.CASCADE, related_name="api_keys"
    )
    key_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=100)
    secret_hash = models.CharField(max_length=200)
    encrypted_secret = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.partner} / {self.name}"


class APIUsageLog(models.Model):
    api_key = models.ForeignKey(
        APIKey, on_delete=models.SET_NULL, blank=True, null=True
    )
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=500)
    status_code = models.PositiveSmallIntegerField()
    response_ms = models.PositiveIntegerField(default=0)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["api_key", "created_at"])]


class WebhookEndpoint(models.Model):
    EVENTS = [
        ("score_updated", "Score updated"),
        ("anomaly_flagged", "Anomaly flagged"),
    ]
    partner = models.ForeignKey(
        ChannelPartner, on_delete=models.CASCADE, related_name="webhooks"
    )
    url = models.URLField()
    event = models.CharField(max_length=40, choices=EVENTS)
    secret_hash = models.CharField(max_length=200)
    encrypted_secret = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
