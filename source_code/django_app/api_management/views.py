import time

from companies.models import DimCompany, FactMlScore
from dashboard.services import company_full_payload
from django.db.models import OuterRef, Subquery
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
    throttle_classes,
)
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .authentication import HMACAPIKeyAuthentication
from .crypto import create_secret
from .models import APIKey, APIUsageLog, ChannelPartner, WebhookEndpoint
from .serializers import APIKeyCreateSerializer, WebhookSerializer
from .throttling import PartnerTierThrottle


def partner_endpoint(view):
    view = authentication_classes([HMACAPIKeyAuthentication])(view)
    view = throttle_classes([PartnerTierThrottle])(view)
    return api_view(["GET"])(view)


def log_usage(request, response, started):
    APIUsageLog.objects.create(
        api_key=request.auth,
        method=request.method,
        path=request.get_full_path()[:500],
        status_code=response.status_code,
        response_ms=int((time.perf_counter() - started) * 1000),
        ip_address=request.META.get("REMOTE_ADDR"),
    )
    return response


@partner_endpoint
def company_full(request, symbol):
    started = time.perf_counter()
    try:
        response = Response(company_full_payload(symbol))
    except DimCompany.DoesNotExist:
        response = Response({"detail": "Company not found."}, status=404)
    return log_usage(request, response, started)


@partner_endpoint
def bulk_financials(request):
    started = time.perf_counter()
    symbols = [
        s.strip().upper()
        for s in request.GET.get("symbols", "").split(",")
        if s.strip()
    ][:25]
    response = Response(
        [
            company_full_payload(s)
            for s in symbols
            if DimCompany.objects.filter(symbol=s).exists()
        ]
    )
    return log_usage(request, response, started)


@partner_endpoint
def partner_screener(request):
    started = time.perf_counter()
    latest = FactMlScore.objects.filter(symbol=OuterRef("symbol")).order_by(
        "-computed_at"
    )
    companies = DimCompany.objects.annotate(
        overall_score=Subquery(latest.values("overall_score")[:1]),
        health_label=Subquery(latest.values("health_label")[:1]),
    )
    if request.GET.get("sector"):
        companies = companies.filter(sector=request.GET["sector"])
    if request.GET.get("health_label"):
        companies = companies.filter(health_label=request.GET["health_label"])
    if request.GET.get("min_roe"):
        companies = companies.filter(roe_pct__gte=request.GET["min_roe"])
    if request.GET.get("max_de"):
        companies = companies.filter(
            factbalancesheet__debt_to_equity__lte=request.GET["max_de"]
        )
    if request.GET.get("min_sales_growth"):
        companies = companies.filter(
            factanalysis__period_label="3Y",
            factanalysis__compounded_sales_growth_pct__gte=request.GET[
                "min_sales_growth"
            ],
        )
    data = list(
        companies.distinct().values(
            "symbol",
            "company_name",
            "sector",
            "roe_pct",
            "overall_score",
            "health_label",
        )
    )
    return log_usage(request, Response(data), started)


@partner_endpoint
def scores(request):
    started = time.perf_counter()
    data = list(
        FactMlScore.objects.select_related("symbol")
        .order_by("-computed_at")
        .values(
            "symbol_id",
            "symbol__company_name",
            "symbol__sector",
            "computed_at",
            "overall_score",
            "profitability_score",
            "growth_score",
            "leverage_score",
            "cashflow_score",
            "dividend_score",
            "trend_score",
            "health_label",
        )
    )
    return log_usage(request, Response(data), started)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def create_key(request):
    serializer = APIKeyCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    partner = ChannelPartner.objects.get(pk=serializer.validated_data["partner_id"])
    secret, secret_hash, encrypted = create_secret()
    api_key = APIKey.objects.create(
        partner=partner,
        name=serializer.validated_data["name"],
        secret_hash=secret_hash,
        encrypted_secret=encrypted,
    )
    return Response(
        {
            "key_id": api_key.key_id,
            "secret": secret,
            "warning": "Store this secret now; it will not be shown again.",
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "POST"])
@authentication_classes([HMACAPIKeyAuthentication])
@throttle_classes([PartnerTierThrottle])
def webhooks(request):
    if request.method == "GET":
        data = WebhookSerializer(
            WebhookEndpoint.objects.filter(partner=request.partner), many=True
        ).data
        return Response(data)
    serializer = WebhookSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    secret, secret_hash, encrypted = create_secret()
    webhook = serializer.save(
        partner=request.partner,
        secret_hash=secret_hash,
        encrypted_secret=encrypted,
    )
    return Response(
        {
            **WebhookSerializer(webhook).data,
            "secret": secret,
            "warning": "Store this webhook secret now.",
        },
        status=201,
    )
