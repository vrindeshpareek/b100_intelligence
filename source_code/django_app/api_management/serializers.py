import ipaddress
from urllib.parse import urlsplit

from django.conf import settings
from rest_framework import serializers

from .models import ChannelPartner, WebhookEndpoint


class APIKeyCreateSerializer(serializers.Serializer):
    partner_id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)

    def validate_partner_id(self, value):
        if not ChannelPartner.objects.filter(pk=value, is_active=True).exists():
            raise serializers.ValidationError("Active partner not found.")
        return value


class WebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEndpoint
        fields = ["id", "url", "event", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_url(self, value):
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"}:
            raise serializers.ValidationError("Webhook URLs must use HTTP or HTTPS.")
        if not settings.DEBUG and parsed.scheme != "https":
            raise serializers.ValidationError("Webhook URLs must use HTTPS.")
        hostname = (parsed.hostname or "").lower()
        if not settings.DEBUG and hostname in {"localhost", "localhost.localdomain"}:
            raise serializers.ValidationError("Local webhook URLs are not allowed.")
        try:
            address = ipaddress.ip_address(hostname)
        except ValueError:
            address = None
        if not settings.DEBUG and address and not address.is_global:
            raise serializers.ValidationError(
                "Private webhook addresses are not allowed."
            )
        return value


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelPartner
        fields = "__all__"
