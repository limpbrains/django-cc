# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cc', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='label',
            field=models.CharField(max_length=100, unique=True, null=True, verbose_name='Label', blank=True),
        ),
    ]
