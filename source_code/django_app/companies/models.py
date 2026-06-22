from django.db import models


class DimCompany(models.Model):
    symbol = models.CharField(primary_key=True, max_length=20)
    company_name = models.CharField(max_length=255)
    sector = models.CharField(max_length=100, blank=True, null=True)
    sub_sector = models.CharField(max_length=100, blank=True, null=True)
    company_logo = models.TextField(blank=True, null=True)
    website = models.TextField(blank=True, null=True)
    nse_url = models.TextField(blank=True, null=True)
    bse_url = models.TextField(blank=True, null=True)
    face_value = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    book_value = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    about_company = models.TextField(blank=True, null=True)
    chart_link = models.TextField(blank=True, null=True)
    roce_pct = models.DecimalField(
        max_digits=10, decimal_places=4, blank=True, null=True
    )
    roe_pct = models.DecimalField(
        max_digits=10, decimal_places=4, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "dim_company"
        ordering = ["company_name"]

    def __str__(self):
        return f"{self.symbol} - {self.company_name}"


class DimYear(models.Model):
    year_id = models.AutoField(primary_key=True)
    year_label = models.CharField(max_length=30, unique=True)
    fiscal_year = models.IntegerField(blank=True, null=True)
    quarter = models.CharField(max_length=5, blank=True, null=True)
    is_ttm = models.BooleanField(default=False)
    is_half_year = models.BooleanField(default=False)
    sort_order = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "dim_year"
        ordering = ["sort_order"]


class FactProfitLoss(models.Model):
    symbol = models.ForeignKey(DimCompany, models.DO_NOTHING, db_column="symbol")
    year = models.ForeignKey(DimYear, models.DO_NOTHING, db_column="year_id")
    sales = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    expenses = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    operating_profit = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    other_income = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    interest = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    depreciation = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    profit_before_tax = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    tax_pct = models.DecimalField(
        max_digits=10, decimal_places=4, blank=True, null=True
    )
    net_profit = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    opm_pct = models.DecimalField(
        max_digits=10, decimal_places=4, blank=True, null=True
    )
    eps = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    dividend_payout_pct = models.DecimalField(
        max_digits=10, decimal_places=4, blank=True, null=True
    )
    net_profit_margin_pct = models.DecimalField(
        max_digits=10, decimal_places=4, blank=True, null=True
    )
    expense_ratio_pct = models.DecimalField(
        max_digits=10, decimal_places=4, blank=True, null=True
    )
    interest_coverage = models.DecimalField(
        max_digits=12, decimal_places=4, blank=True, null=True
    )
    asset_turnover = models.DecimalField(
        max_digits=12, decimal_places=4, blank=True, null=True
    )
    return_on_assets = models.DecimalField(
        max_digits=12, decimal_places=4, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "fact_profit_loss"
        ordering = ["symbol", "year__sort_order"]


class FactBalanceSheet(models.Model):
    symbol = models.ForeignKey(DimCompany, models.DO_NOTHING, db_column="symbol")
    year = models.ForeignKey(DimYear, models.DO_NOTHING, db_column="year_id")
    equity_capital = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    borrowings = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    reserves = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    other_liabilities = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    total_liabilities = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    fixed_assets = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    cwip = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    investments = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    other_assets = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    total_assets = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    debt_to_equity = models.DecimalField(
        max_digits=12, decimal_places=4, blank=True, null=True
    )
    equity_ratio = models.DecimalField(
        max_digits=10, decimal_places=4, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "fact_balance_sheet"


class FactCashFlow(models.Model):
    symbol = models.ForeignKey(DimCompany, models.DO_NOTHING, db_column="symbol")
    year = models.ForeignKey(DimYear, models.DO_NOTHING, db_column="year_id")
    operating_activity = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    investing_activity = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    financing_activity = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    net_cash_flow = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    free_cash_flow = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    cash_conversion_ratio = models.DecimalField(
        max_digits=12, decimal_places=4, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "fact_cash_flow"


class FactAnalysis(models.Model):
    symbol = models.ForeignKey(DimCompany, models.DO_NOTHING, db_column="symbol")
    period_label = models.CharField(max_length=10)
    compounded_sales_growth_pct = models.DecimalField(
        max_digits=10, decimal_places=4, blank=True, null=True
    )
    compounded_profit_growth_pct = models.DecimalField(
        max_digits=10, decimal_places=4, blank=True, null=True
    )
    stock_price_cagr_pct = models.DecimalField(
        max_digits=10, decimal_places=4, blank=True, null=True
    )
    roe_pct = models.DecimalField(
        max_digits=10, decimal_places=4, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "fact_analysis"


class FactMlScore(models.Model):
    symbol = models.ForeignKey(DimCompany, models.DO_NOTHING, db_column="symbol")
    computed_at = models.DateTimeField(blank=True, null=True)
    overall_score = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True
    )
    profitability_score = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True
    )
    growth_score = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True
    )
    leverage_score = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True
    )
    cashflow_score = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True
    )
    dividend_score = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True
    )
    trend_score = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True
    )
    health_label = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "fact_ml_scores"


class FactProsCons(models.Model):
    symbol = models.ForeignKey(DimCompany, models.DO_NOTHING, db_column="symbol")
    is_pro = models.BooleanField()
    category = models.CharField(max_length=100, blank=True, null=True)
    text = models.TextField()
    source = models.CharField(max_length=20, blank=True, null=True)
    confidence = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    generated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "fact_pros_cons"


class FactDocument(models.Model):
    symbol = models.ForeignKey(DimCompany, models.DO_NOTHING, db_column="symbol")
    fiscal_year = models.IntegerField(blank=True, null=True)
    annual_report = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "fact_documents"
        ordering = ["-fiscal_year"]
