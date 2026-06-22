from accounts.throttling import LoginRateThrottle
from django.test import SimpleTestCase
from django.urls import resolve


class DashboardRouteTests(SimpleTestCase):
    def test_required_routes_resolve(self):
        for path in [
            "/",
            "/companies/",
            "/compare/",
            "/screener/",
            "/company/TCS/",
            "/sector/IT/",
        ]:
            self.assertIsNotNone(resolve(path))

    def test_documents_api_route_resolves(self):
        self.assertEqual(resolve("/api/v1/documents/").url_name, "document-list")

    def test_login_endpoint_uses_hard_login_throttle(self):
        view = resolve("/api/auth/token/").func.view_class
        self.assertEqual(view.throttle_classes, [LoginRateThrottle])
