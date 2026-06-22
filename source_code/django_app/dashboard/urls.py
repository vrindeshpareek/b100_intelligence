from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("companies/", views.company_list, name="company-list"),
    path("company/<str:symbol>/", views.company_detail, name="company-detail"),
    path("compare/", views.compare, name="compare"),
    path("screener/", views.screener, name="screener"),
    path("sector/<path:name>/", views.sector_detail, name="sector-detail"),
]
