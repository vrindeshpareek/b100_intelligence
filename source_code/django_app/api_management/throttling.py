import time

from django.core.cache import cache
from rest_framework.throttling import BaseThrottle

LIMITS = {
    "BASIC": {"minute": 10, "hour": 100, "day": 500},
    "PRO": {"minute": 60, "hour": 1000, "day": 10000},
    "ENTERPRISE": {"minute": 300, "hour": 10000, "day": 100000},
}
WINDOWS = {"minute": 60, "hour": 3600, "day": 86400}


class PartnerTierThrottle(BaseThrottle):
    def allow_request(self, request, view):
        api_key = request.auth
        if not api_key:
            return False
        limits = LIMITS[api_key.partner.tier]
        now = int(time.time())
        for window, seconds in WINDOWS.items():
            bucket = now // seconds
            key = f"partner-rate:{api_key.key_id}:{window}:{bucket}"
            if cache.add(key, 1, seconds + 5):
                count = 1
            else:
                try:
                    count = cache.incr(key)
                except ValueError:
                    # The key may expire between add() and incr().
                    cache.set(key, 1, seconds + 5)
                    count = 1
            if count > limits[window]:
                self.wait_seconds = seconds - (now % seconds)
                return False
        return True

    def wait(self):
        return getattr(self, "wait_seconds", None)
