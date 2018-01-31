from __future__ import unicode_literals

from django.db import models


class CompanyDetails(models.Model):
    name = models.CharField(max_length=50)
    yahoo_sht = models.CharField(max_length=50, primary_key=True)
    sector = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}: {}".format(self.name, self.yahoo_sht)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super(CompanyDetails, self).save(*args, **kwargs)


class CompanyStocks(models.Model):
    id = models.BigIntegerField(primary_key=True)
    open = models.DecimalField(max_digits=20, decimal_places=6)
    close = models.DecimalField(max_digits=20, decimal_places=6)
    adj_close = models.DecimalField(max_digits=20, decimal_places=6)
    high = models.DecimalField(max_digits=20, decimal_places=6)
    low = models.DecimalField(max_digits=20, decimal_places=6)
    record_date = models.DateField()
    volume = models.DecimalField(max_digits=20, decimal_places=6)
    ticker = models.ForeignKey(CompanyDetails, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}: {}".format(self.ticker.name, self.stock_id)


