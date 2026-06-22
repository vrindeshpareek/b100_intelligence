from companies.models import (
    DimCompany,
    FactAnalysis,
    FactBalanceSheet,
    FactCashFlow,
    FactDocument,
    FactMlScore,
    FactProfitLoss,
    FactProsCons,
)
from dashboard.services import company_chart_payload, company_full_payload
from django.db.models import Avg, Count, Sum
from django.views.decorators.cache import cache_page
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .serializers import (
    AnalysisSerializer,
    BalanceSheetSerializer,
    CashFlowSerializer,
    CompanySerializer,
    DocumentSerializer,
    MlScoreSerializer,
    ProfitLossSerializer,
    ProsConsSerializer,
)


class CompanyViewSet(ReadOnlyModelViewSet):
    queryset = DimCompany.objects.all()
    serializer_class = CompanySerializer
    lookup_field = "symbol"
    search_fields = ["symbol", "company_name", "sector", "sub_sector"]
    ordering_fields = ["symbol", "company_name", "sector", "roe_pct", "roce_pct"]
    filterset_fields = ["sector", "sub_sector"]

    @action(detail=True)
    def snapshot(self, request, symbol=None):
        company = self.get_object()
        latest_pl = (
            FactProfitLoss.objects.filter(symbol=company)
            .select_related("year")
            .order_by("-year__sort_order")
            .first()
        )
        latest_bs = (
            FactBalanceSheet.objects.filter(symbol=company)
            .select_related("year")
            .order_by("-year__sort_order")
            .first()
        )
        score = (
            FactMlScore.objects.filter(symbol=company).order_by("-computed_at").first()
        )
        return Response(
            {
                "company": CompanySerializer(company).data,
                "latest_profit_loss": (
                    ProfitLossSerializer(latest_pl).data if latest_pl else None
                ),
                "latest_balance_sheet": (
                    BalanceSheetSerializer(latest_bs).data if latest_bs else None
                ),
                "latest_score": MlScoreSerializer(score).data if score else None,
            }
        )

    @action(detail=True)
    def timeseries(self, request, symbol=None):
        company = self.get_object()
        return Response(
            {
                "profit_loss": ProfitLossSerializer(
                    FactProfitLoss.objects.filter(symbol=company)
                    .select_related("year")
                    .order_by("year__sort_order"),
                    many=True,
                ).data,
                "balance_sheet": BalanceSheetSerializer(
                    FactBalanceSheet.objects.filter(symbol=company)
                    .select_related("year")
                    .order_by("year__sort_order"),
                    many=True,
                ).data,
                "cash_flow": CashFlowSerializer(
                    FactCashFlow.objects.filter(symbol=company)
                    .select_related("year")
                    .order_by("year__sort_order"),
                    many=True,
                ).data,
                "analysis": AnalysisSerializer(
                    FactAnalysis.objects.filter(symbol=company), many=True
                ).data,
            }
        )

    @action(detail=True)
    def charts(self, request, symbol=None):
        self.get_object()
        return Response(company_chart_payload(symbol))

    @action(detail=True)
    def full(self, request, symbol=None):
        self.get_object()
        return Response(company_full_payload(symbol))


class ProfitLossViewSet(ReadOnlyModelViewSet):
    queryset = FactProfitLoss.objects.select_related("symbol", "year").all()
    serializer_class = ProfitLossSerializer
    filterset_fields = ["symbol", "year__fiscal_year", "year__year_label"]
    ordering_fields = ["sales", "net_profit", "opm_pct", "eps", "year__sort_order"]


class BalanceSheetViewSet(ReadOnlyModelViewSet):
    queryset = FactBalanceSheet.objects.select_related("symbol", "year").all()
    serializer_class = BalanceSheetSerializer
    filterset_fields = ["symbol", "year__fiscal_year", "year__year_label"]
    ordering_fields = [
        "total_assets",
        "borrowings",
        "debt_to_equity",
        "year__sort_order",
    ]


class CashFlowViewSet(ReadOnlyModelViewSet):
    queryset = FactCashFlow.objects.select_related("symbol", "year").all()
    serializer_class = CashFlowSerializer
    filterset_fields = ["symbol", "year__fiscal_year", "year__year_label"]
    ordering_fields = [
        "operating_activity",
        "free_cash_flow",
        "cash_conversion_ratio",
        "year__sort_order",
    ]


class AnalysisViewSet(ReadOnlyModelViewSet):
    queryset = FactAnalysis.objects.select_related("symbol").all()
    serializer_class = AnalysisSerializer
    filterset_fields = ["symbol", "period_label"]


class MlScoreViewSet(ReadOnlyModelViewSet):
    queryset = FactMlScore.objects.select_related("symbol").all()
    serializer_class = MlScoreSerializer
    filterset_fields = ["symbol", "health_label", "symbol__sector"]
    ordering_fields = [
        "overall_score",
        "profitability_score",
        "growth_score",
        "leverage_score",
        "cashflow_score",
    ]


class ProsConsViewSet(ReadOnlyModelViewSet):
    queryset = FactProsCons.objects.select_related("symbol").all()
    serializer_class = ProsConsSerializer
    filterset_fields = ["symbol", "is_pro", "category", "source"]


class DocumentViewSet(ReadOnlyModelViewSet):
    queryset = FactDocument.objects.select_related("symbol").all()
    serializer_class = DocumentSerializer
    filterset_fields = ["symbol", "fiscal_year"]
    ordering_fields = ["fiscal_year"]


@api_view(["GET"])
@cache_page(3600)
def market_summary(request):
    return Response(
        {
            "companies": DimCompany.objects.count(),
            "sectors": DimCompany.objects.values("sector").distinct().count(),
            "latest_scores": FactMlScore.objects.count(),
            "avg_health_score": FactMlScore.objects.aggregate(
                value=Avg("overall_score")
            )["value"],
            "sector_distribution": list(
                DimCompany.objects.values("sector")
                .annotate(company_count=Count("symbol"))
                .order_by("sector")
            ),
            "revenue_by_sector": list(
                FactProfitLoss.objects.values("symbol__sector")
                .annotate(total_sales=Sum("sales"), total_profit=Sum("net_profit"))
                .order_by("symbol__sector")
            ),
        }
    )
