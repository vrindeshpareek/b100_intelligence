import hashlib
import hmac
import time
import uuid

import requests

BASE_URL = "http://localhost:8000"
PATH = "/api/partner/v1/scores/"
KEY_ID = "replace-with-key-id"
SECRET = "replace-with-one-time-secret"

timestamp = str(int(time.time()))
nonce = str(uuid.uuid4())
body_hash = hashlib.sha256(b"").hexdigest()
canonical = "\n".join(["GET", PATH, timestamp, nonce, body_hash])
signature = hmac.new(SECRET.encode(), canonical.encode(), hashlib.sha256).hexdigest()

response = requests.get(
    BASE_URL + PATH,
    headers={
        "X-API-Key-ID": KEY_ID,
        "X-Timestamp": timestamp,
        "X-Nonce": nonce,
        "X-Signature": signature,
    },
    timeout=30,
)
print(response.status_code, response.text)
