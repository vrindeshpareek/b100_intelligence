import hashlib
import hmac
import time

from django.core.cache import cache
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from .crypto import decrypt_secret
from .models import APIKey


class HMACAPIKeyAuthentication(BaseAuthentication):
    max_clock_skew = 300

    def authenticate_header(self, request):
        """Make DRF return 401 (not 403) for failed HMAC authentication."""
        return "HMAC"

    def authenticate(self, request):
        key_id = request.headers.get("X-API-Key-ID")
        timestamp = request.headers.get("X-Timestamp")
        signature = request.headers.get("X-Signature")
        nonce = request.headers.get("X-Nonce")
        if not all([key_id, timestamp, signature, nonce]):
            raise exceptions.AuthenticationFailed(
                "Missing HMAC authentication headers."
            )
        try:
            timestamp_int = int(timestamp)
        except ValueError as exc:
            raise exceptions.AuthenticationFailed("Invalid timestamp.") from exc
        if abs(int(time.time()) - timestamp_int) > self.max_clock_skew:
            raise exceptions.AuthenticationFailed("Expired timestamp.")
        try:
            api_key = APIKey.objects.select_related("partner").get(
                key_id=key_id, is_active=True, partner__is_active=True
            )
        except APIKey.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed("Unknown API key.") from exc
        body_hash = hashlib.sha256(request.body or b"").hexdigest()
        canonical = "\n".join(
            [
                request.method.upper(),
                request.get_full_path(),
                timestamp,
                nonce,
                body_hash,
            ]
        )
        expected = hmac.new(
            decrypt_secret(api_key.encrypted_secret).encode(),
            canonical.encode(),
            hashlib.sha256,
        ).hexdigest()
        if not secrets_compare(expected, signature):
            raise exceptions.AuthenticationFailed("Invalid signature.")
        # Consume the nonce only after authenticating the signature. Otherwise an
        # attacker could pre-empt a legitimate request by submitting its nonce
        # with a bogus signature.
        nonce_key = f"hmac-nonce:{key_id}:{nonce}"
        if not cache.add(nonce_key, True, self.max_clock_skew):
            raise exceptions.AuthenticationFailed("Nonce has already been used.")
        APIKey.objects.filter(pk=api_key.pk).update(last_used_at=timezone.now())
        request.partner = api_key.partner
        return (None, api_key)


def secrets_compare(left, right):
    return hmac.compare_digest(str(left), str(right))
