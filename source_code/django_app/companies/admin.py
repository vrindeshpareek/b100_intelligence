from django.contrib import admin

from .models import DimCompany


@admin.register(DimCompany)
class DimCompanyAdmin(admin.ModelAdmin):
    list_display = ("symbol", "company_name", "sector", "sub_sector")
    search_fields = ("symbol", "company_name", "sector")
