import hashlib
import hmac
import json
import time
from urllib.request import Request, urlopen

from celery import shared_task

from .crypto import decrypt_secret
from .models import WebhookEndpoint


@shared_task
def dispatch_webhook(event, payload):
    delivered = 0
    body = json.dumps({"event": event, "data": payload}, separators=(",", ":")).encode()
    timestamp = str(int(time.time()))
    for webhook in WebhookEndpoint.objects.filter(event=event, is_active=True):
        signature = hmac.new(
            decrypt_secret(webhook.encrypted_secret).encode(),
            timestamp.encode() + b"." + body,
            hashlib.sha256,
        ).hexdigest()
        request = Request(
            webhook.url,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-B100-Event": event,
                "X-B100-Timestamp": timestamp,
                "X-B100-Signature": signature,
            },
        )
        try:
            # WebhookSerializer restricts persisted URLs to HTTP(S), HTTPS in
            # production, and rejects literal private addresses.
            with urlopen(request, timeout=10) as response:  # nosec B310
                delivered += int(200 <= response.status < 300)
        except Exception:
            continue
    return {"delivered": delivered}
