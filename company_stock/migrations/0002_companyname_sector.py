# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-01-29 17:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_stock', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyname',
            name='sector',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]
