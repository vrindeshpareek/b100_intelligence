from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("companies", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="factprofitloss",
            name="other_income",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=18, null=True
            ),
        ),
        migrations.AddField(
            model_name="factprofitloss",
            name="interest",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=18, null=True
            ),
        ),
        migrations.AddField(
            model_name="factprofitloss",
            name="depreciation",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=18, null=True
            ),
        ),
        migrations.AddField(
            model_name="factprofitloss",
            name="profit_before_tax",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=18, null=True
            ),
        ),
        migrations.AddField(
            model_name="factprofitloss",
            name="tax_pct",
            field=models.DecimalField(
                blank=True, decimal_places=4, max_digits=10, null=True
            ),
        ),
        migrations.AddField(
            model_name="factprofitloss",
            name="expense_ratio_pct",
            field=models.DecimalField(
                blank=True, decimal_places=4, max_digits=10, null=True
            ),
        ),
    ]
