# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-01-31 16:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TwitterClassiferAlgo',
            fields=[
                ('classifer_name', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('classifier_pickled_data', models.BinaryField(default=None)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]