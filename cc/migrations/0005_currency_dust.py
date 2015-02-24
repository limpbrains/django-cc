# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('cc', '0004_txid_not_uniq'),
    ]

    operations = [
        migrations.AddField(
            model_name='currency',
            name='dust',
            field=models.DecimalField(default=Decimal('0.0000543'), verbose_name='Dust', max_digits=18, decimal_places=8),
            preserve_default=True,
        ),
    ]
