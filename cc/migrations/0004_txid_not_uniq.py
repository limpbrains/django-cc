# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cc', '0003_auto_20150106_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='address',
            field=models.CharField(default='', max_length=50, verbose_name='Address'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='transaction',
            name='txid',
            field=models.CharField(max_length=100, verbose_name='Txid'),
        ),
        migrations.AlterUniqueTogether(
            name='transaction',
            unique_together=set([('txid', 'address')]),
        ),
    ]
