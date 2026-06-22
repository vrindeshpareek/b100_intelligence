from django.urls import path

from . import views

urlpatterns = [
    path(
        "companies/<str:symbol>/full/", views.company_full, name="partner-company-full"
    ),
    path("bulk-financials/", views.bulk_financials, name="partner-bulk-financials"),
    path("screener/", views.partner_screener, name="partner-screener"),
    path("scores/", views.scores, name="partner-scores"),
    path("keys/", views.create_key, name="partner-create-key"),
    path("webhooks/", views.webhooks, name="partner-webhooks"),
]
