from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, render

from .models import DimCompany, FactMlScore, FactProfitLoss


def dashboard(request):
    latest_scores = (
        FactMlScore.objects.order_by("symbol_id", "-computed_at").distinct("symbol_id")
        if False
        else FactMlScore.objects.all()
    )
    context = {
        "company_count": DimCompany.objects.count(),
        "sector_count": DimCompany.objects.values("sector").distinct().count(),
        "avg_score": latest_scores.aggregate(value=Avg("overall_score"))["value"],
        "top_scores": latest_scores.select_related("symbol").order_by("-overall_score")[
            :10
        ],
        "sectors": DimCompany.objects.values("sector")
        .annotate(count=Count("symbol"))
        .order_by("sector"),
    }
    return render(request, "companies/dashboard.html", context)


def company_detail(request, symbol):
    company = get_object_or_404(DimCompany, symbol=symbol.upper())
    pl_rows = (
        FactProfitLoss.objects.filter(symbol=company)
        .select_related("year")
        .order_by("year__sort_order")
    )
    score = FactMlScore.objects.filter(symbol=company).order_by("-computed_at").first()
    return render(
        request,
        "companies/company_detail.html",
        {"company": company, "pl_rows": pl_rows, "score": score},
    )
