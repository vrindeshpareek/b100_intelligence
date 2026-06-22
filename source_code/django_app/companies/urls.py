from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("companies/<str:symbol>/", views.company_detail, name="company-detail"),
]
