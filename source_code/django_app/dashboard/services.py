from decimal import Decimal

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
from django.core.cache import cache
from django.db.models import OuterRef, Subquery


def number(value):
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    return value


def latest_score_subquery():
    return FactMlScore.objects.filter(symbol=OuterRef("symbol")).order_by(
        "-computed_at"
    )


def enriched_companies():
    scores = latest_score_subquery()
    return DimCompany.objects.annotate(
        health_score=Subquery(scores.values("overall_score")[:1]),
        health_label=Subquery(scores.values("health_label")[:1]),
    )


def company_chart_payload(symbol):
    cache_key = f"company-charts:{symbol.upper()}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    company = DimCompany.objects.get(symbol=symbol.upper())
    pl = list(
        FactProfitLoss.objects.filter(symbol=company, year__is_ttm=False)
        .select_related("year")
        .order_by("year__sort_order")
    )
    bs = {
        row.year_id: row
        for row in FactBalanceSheet.objects.filter(symbol=company, year__is_ttm=False)
        .select_related("year")
        .order_by("year__sort_order")
    }
    cf = {
        row.year_id: row
        for row in FactCashFlow.objects.filter(symbol=company, year__is_ttm=False)
        .select_related("year")
        .order_by("year__sort_order")
    }
    analysis = list(
        FactAnalysis.objects.filter(symbol=company).order_by("period_label")
    )
    latest_score = (
        FactMlScore.objects.filter(symbol=company).order_by("-computed_at").first()
    )

    years = [row.year.year_label for row in pl]
    balance_rows = [bs.get(row.year_id) for row in pl]
    cash_rows = [cf.get(row.year_id) for row in pl]

    payload = {
        "symbol": company.symbol,
        "years": years,
        "revenue_profit": {
            "sales": [number(row.sales) for row in pl],
            "net_profit": [number(row.net_profit) for row in pl],
            "opm_pct": [number(row.opm_pct) for row in pl],
        },
        "balance_sheet": {
            "equity_reserves": [
                number((row.equity_capital or 0) + (row.reserves or 0)) if row else None
                for row in balance_rows
            ],
            "borrowings": [
                number(row.borrowings) if row else None for row in balance_rows
            ],
            "other_liabilities": [
                number(row.other_liabilities) if row else None for row in balance_rows
            ],
            "reserves": [number(row.reserves) if row else None for row in balance_rows],
        },
        "cash_flow": {
            "operating": [
                number(row.operating_activity) if row else None for row in cash_rows
            ],
            "investing": [
                number(row.investing_activity) if row else None for row in cash_rows
            ],
            "financing": [
                number(row.financing_activity) if row else None for row in cash_rows
            ],
        },
        "eps_dividend": {
            "eps": [number(row.eps) for row in pl],
            "dividend_payout_pct": [number(row.dividend_payout_pct) for row in pl],
        },
        "margins": {
            "opm_pct": [number(row.opm_pct) for row in pl],
            "net_profit_margin_pct": [number(row.net_profit_margin_pct) for row in pl],
        },
        "cagr_radar": {
            "periods": [row.period_label for row in analysis],
            "sales": [number(row.compounded_sales_growth_pct) for row in analysis],
            "profit": [number(row.compounded_profit_growth_pct) for row in analysis],
            "stock": [number(row.stock_price_cagr_pct) for row in analysis],
            "roe": [number(row.roe_pct) for row in analysis],
        },
        "health": {
            "overall": number(latest_score.overall_score) if latest_score else None,
            "label": latest_score.health_label if latest_score else None,
            "profitability": (
                number(latest_score.profitability_score) if latest_score else None
            ),
            "growth": number(latest_score.growth_score) if latest_score else None,
            "leverage": number(latest_score.leverage_score) if latest_score else None,
            "cashflow": number(latest_score.cashflow_score) if latest_score else None,
            "dividend": number(latest_score.dividend_score) if latest_score else None,
            "trend": number(latest_score.trend_score) if latest_score else None,
        },
    }
    cache.set(cache_key, payload, 3600)
    return payload


def company_full_payload(symbol):
    company = DimCompany.objects.get(symbol=symbol.upper())
    return {
        "company": {
            "symbol": company.symbol,
            "company_name": company.company_name,
            "sector": company.sector,
            "sub_sector": company.sub_sector,
            "website": company.website,
            "roe_pct": number(company.roe_pct),
            "roce_pct": number(company.roce_pct),
        },
        "charts": company_chart_payload(symbol),
        "pros_cons": list(
            FactProsCons.objects.filter(symbol=company).values(
                "is_pro", "category", "text", "source", "confidence"
            )
        ),
        "documents": list(
            FactDocument.objects.filter(symbol=company).values(
                "fiscal_year", "annual_report"
            )
        ),
    }
