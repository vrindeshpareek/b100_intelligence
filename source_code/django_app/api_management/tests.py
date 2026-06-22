import hashlib
import hmac
import time
import uuid

from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .crypto import create_secret
from .models import APIKey, ChannelPartner
from .serializers import WebhookSerializer


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
class HMACAuthenticationTests(TestCase):
    def setUp(self):
        cache.clear()
        self.partner = ChannelPartner.objects.create(
            name="Partner", contact_email="p@example.com", tier="BASIC"
        )
        self.secret, secret_hash, encrypted = create_secret()
        self.api_key = APIKey.objects.create(
            partner=self.partner,
            name="Test",
            secret_hash=secret_hash,
            encrypted_secret=encrypted,
        )
        self.client = APIClient()

    def headers(self, path, secret=None, timestamp=None, nonce=None):
        timestamp = str(timestamp or int(time.time()))
        nonce = nonce or str(uuid.uuid4())
        body_hash = hashlib.sha256(b"").hexdigest()
        canonical = "\n".join(["GET", path, timestamp, nonce, body_hash])
        signature = hmac.new(
            (secret or self.secret).encode(), canonical.encode(), hashlib.sha256
        ).hexdigest()
        return {
            "HTTP_X_API_KEY_ID": str(self.api_key.key_id),
            "HTTP_X_TIMESTAMP": timestamp,
            "HTTP_X_NONCE": nonce,
            "HTTP_X_SIGNATURE": signature,
        }

    def test_valid_signature_reaches_view(self):
        path = "/api/partner/v1/webhooks/"
        response = self.client.get(path, **self.headers(path))
        self.assertNotEqual(response.status_code, 401)

    def test_tampered_signature_is_rejected(self):
        path = "/api/partner/v1/webhooks/"
        response = self.client.get(path, **self.headers(path, secret="wrong"))
        self.assertEqual(response.status_code, 401)

    def test_tampered_signature_does_not_consume_nonce(self):
        path = "/api/partner/v1/webhooks/"
        nonce = str(uuid.uuid4())
        bad_headers = self.headers(path, secret="wrong", nonce=nonce)
        self.assertEqual(self.client.get(path, **bad_headers).status_code, 401)
        valid_headers = self.headers(
            path, timestamp=bad_headers["HTTP_X_TIMESTAMP"], nonce=nonce
        )
        self.assertNotEqual(self.client.get(path, **valid_headers).status_code, 401)

    def test_expired_timestamp_is_rejected(self):
        path = "/api/partner/v1/webhooks/"
        response = self.client.get(
            path, **self.headers(path, timestamp=int(time.time()) - 600)
        )
        self.assertEqual(response.status_code, 401)

    def test_replayed_nonce_is_rejected(self):
        path = "/api/partner/v1/webhooks/"
        nonce = str(uuid.uuid4())
        headers = self.headers(path, nonce=nonce)
        self.client.get(path, **headers)
        response = self.client.get(path, **headers)
        self.assertEqual(response.status_code, 401)


class WebhookValidationTests(TestCase):
    @override_settings(DEBUG=False)
    def test_production_webhook_requires_https(self):
        serializer = WebhookSerializer(
            data={"url": "http://example.com/hook", "event": "score_updated"}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("url", serializer.errors)

    @override_settings(DEBUG=False)
    def test_production_webhook_rejects_private_address(self):
        serializer = WebhookSerializer(
            data={"url": "https://127.0.0.1/hook", "event": "score_updated"}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("url", serializer.errors)

    @override_settings(DEBUG=False)
    def test_production_webhook_accepts_public_https(self):
        serializer = WebhookSerializer(
            data={"url": "https://example.com/hook", "event": "score_updated"}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
