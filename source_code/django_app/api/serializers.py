from companies.models import (
    DimCompany,
    DimYear,
    FactAnalysis,
    FactBalanceSheet,
    FactCashFlow,
    FactDocument,
    FactMlScore,
    FactProfitLoss,
    FactProsCons,
)
from rest_framework import serializers


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = DimCompany
        fields = "__all__"


class YearSerializer(serializers.ModelSerializer):
    class Meta:
        model = DimYear
        fields = "__all__"


class ProfitLossSerializer(serializers.ModelSerializer):
    year_label = serializers.CharField(source="year.year_label", read_only=True)

    class Meta:
        model = FactProfitLoss
        fields = "__all__"


class BalanceSheetSerializer(serializers.ModelSerializer):
    year_label = serializers.CharField(source="year.year_label", read_only=True)

    class Meta:
        model = FactBalanceSheet
        fields = "__all__"


class CashFlowSerializer(serializers.ModelSerializer):
    year_label = serializers.CharField(source="year.year_label", read_only=True)

    class Meta:
        model = FactCashFlow
        fields = "__all__"


class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactAnalysis
        fields = "__all__"


class MlScoreSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="symbol.company_name", read_only=True)
    sector = serializers.CharField(source="symbol.sector", read_only=True)

    class Meta:
        model = FactMlScore
        fields = "__all__"


class ProsConsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactProsCons
        fields = "__all__"


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactDocument
        fields = "__all__"
