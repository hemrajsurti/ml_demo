# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-01-29 18:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_stock', '0004_auto_20180129_2338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companydetails',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
