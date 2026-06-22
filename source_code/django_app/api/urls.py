from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("companies", views.CompanyViewSet, basename="company")
router.register("profit-loss", views.ProfitLossViewSet, basename="profit-loss")
router.register("balance-sheet", views.BalanceSheetViewSet, basename="balance-sheet")
router.register("cash-flow", views.CashFlowViewSet, basename="cash-flow")
router.register("analysis", views.AnalysisViewSet, basename="analysis")
router.register("scores", views.MlScoreViewSet, basename="score")
router.register("pros-cons", views.ProsConsViewSet, basename="pros-cons")
router.register("documents", views.DocumentViewSet, basename="document")

urlpatterns = [
    path("market-summary/", views.market_summary, name="market-summary"),
]
urlpatterns += router.urls
