from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from .tasks import dispatch_webhook


class WebhookTaskTests(SimpleTestCase):
    @patch("api_management.tasks.urlopen")
    @patch("api_management.tasks.decrypt_secret", return_value="webhook-secret")
    @patch("api_management.tasks.WebhookEndpoint.objects")
    def test_dispatch_webhook_signs_and_delivers(self, objects, decrypt, urlopen):
        objects.filter.return_value = [
            SimpleNamespace(
                url="https://example.com/hook", encrypted_secret="ciphertext"
            )
        ]
        response = MagicMock(status=204)
        urlopen.return_value.__enter__.return_value = response

        result = dispatch_webhook.run("score_updated", {"symbol": "TCS"})

        self.assertEqual(result, {"delivered": 1})
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://example.com/hook")
        self.assertTrue(request.headers["X-b100-signature"])

    @patch("api_management.tasks.urlopen", side_effect=OSError("offline"))
    @patch("api_management.tasks.decrypt_secret", return_value="webhook-secret")
    @patch("api_management.tasks.WebhookEndpoint.objects")
    def test_dispatch_webhook_continues_after_delivery_error(
        self, objects, decrypt, urlopen
    ):
        objects.filter.return_value = [
            SimpleNamespace(
                url="https://example.com/hook", encrypted_secret="ciphertext"
            )
        ]
        self.assertEqual(dispatch_webhook.run("anomaly_flagged", {}), {"delivered": 0})
