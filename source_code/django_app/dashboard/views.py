from companies.models import DimCompany, FactDocument, FactMlScore, FactProsCons
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, render

from .services import company_chart_payload, enriched_companies


def home(request):
    companies = enriched_companies()
    return render(
        request,
        "dashboard/home.html",
        {
            "featured": companies.order_by("-health_score")[:8],
            "sectors": DimCompany.objects.values("sector")
            .annotate(count=Count("symbol"))
            .order_by("-count"),
            "insights": FactProsCons.objects.select_related("symbol").order_by(
                "-generated_at"
            )[:8],
            "company_count": companies.count(),
            "avg_score": FactMlScore.objects.aggregate(value=Avg("overall_score"))[
                "value"
            ],
        },
    )


def company_list(request):
    companies = enriched_companies()
    search = request.GET.get("q", "").strip()
    sector = request.GET.get("sector", "").strip()
    health = request.GET.get("health", "").strip()
    debt = request.GET.get("debt", "").strip()
    ordering = request.GET.get("sort", "-health_score")
    if search:
        companies = companies.filter(
            Q(symbol__icontains=search) | Q(company_name__icontains=search)
        )
    if sector:
        companies = companies.filter(sector=sector)
    if health:
        companies = companies.filter(health_label=health)
    if debt:
        threshold = {"low": 0.5, "medium": 2}.get(debt)
        if debt == "high":
            companies = companies.filter(factbalancesheet__debt_to_equity__gt=2)
        elif threshold is not None:
            companies = companies.filter(
                factbalancesheet__debt_to_equity__lte=threshold
            )
    allowed = {
        "company_name",
        "-company_name",
        "roe_pct",
        "-roe_pct",
        "health_score",
        "-health_score",
    }
    companies = companies.order_by(
        ordering if ordering in allowed else "-health_score"
    ).distinct()
    return render(
        request,
        "dashboard/company_list.html",
        {
            "companies": companies,
            "sectors": DimCompany.objects.values_list("sector", flat=True)
            .distinct()
            .order_by("sector"),
        },
    )


def company_detail(request, symbol):
    company = get_object_or_404(DimCompany, symbol=symbol.upper())
    return render(
        request,
        "dashboard/company_detail.html",
        {
            "company": company,
            "score": FactMlScore.objects.filter(symbol=company)
            .order_by("-computed_at")
            .first(),
            "pros": FactProsCons.objects.filter(symbol=company, is_pro=True),
            "cons": FactProsCons.objects.filter(symbol=company, is_pro=False),
            "documents": FactDocument.objects.filter(symbol=company),
        },
    )


def compare(request):
    symbols = [s.upper() for s in request.GET.getlist("symbols") if s][:4]
    selected = enriched_companies().filter(symbol__in=symbols)
    payloads = [company_chart_payload(symbol) for symbol in symbols]
    return render(
        request,
        "dashboard/compare.html",
        {
            "companies": DimCompany.objects.all(),
            "selected": selected,
            "payloads": payloads,
            "symbols": symbols,
        },
    )


def screener(request):
    companies = enriched_companies()
    sector = request.GET.get("sector")
    health = request.GET.get("health")
    min_roe = request.GET.get("min_roe")
    max_de = request.GET.get("max_de")
    min_growth = request.GET.get("min_growth")
    if sector:
        companies = companies.filter(sector=sector)
    if health:
        companies = companies.filter(health_label=health)
    if min_roe:
        companies = companies.filter(roe_pct__gte=min_roe)
    if max_de:
        companies = companies.filter(factbalancesheet__debt_to_equity__lte=max_de)
    if min_growth:
        companies = companies.filter(
            factanalysis__period_label="3Y",
            factanalysis__compounded_sales_growth_pct__gte=min_growth,
        )
    return render(
        request,
        "dashboard/screener.html",
        {
            "companies": companies.distinct().order_by("-health_score"),
            "sectors": DimCompany.objects.values_list("sector", flat=True)
            .distinct()
            .order_by("sector"),
        },
    )


def sector_detail(request, name):
    companies = enriched_companies().filter(sector=name)
    return render(
        request,
        "dashboard/sector_detail.html",
        {"sector": name, "companies": companies},
    )
