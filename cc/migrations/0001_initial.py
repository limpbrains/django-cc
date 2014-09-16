# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('address', models.CharField(max_length=50, serialize=False, verbose_name='Address', primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('label', models.CharField(default=None, max_length=50, null=True, verbose_name='Label', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('ticker', models.CharField(default=b'BTC', max_length=4, serialize=False, verbose_name='Ticker', primary_key=True)),
                ('label', models.CharField(default=b'Bitcoin', unique=True, max_length=20, verbose_name='Label')),
                ('magicbyte', models.CommaSeparatedIntegerField(default=b'0,5', max_length=10, verbose_name='Magicbytes')),
                ('last_block', models.PositiveIntegerField(default=0, null=True, verbose_name='Last block', blank=True)),
                ('api_url', models.CharField(default=b'http://localhost:8332', max_length=100, null=True, verbose_name='API hostname', blank=True)),
            ],
            options={
                'verbose_name_plural': 'currencies',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created')),
                ('balance', models.DecimalField(default=0, verbose_name='Balance', max_digits=18, decimal_places=8)),
                ('holded', models.DecimalField(default=0, verbose_name='Holded', max_digits=18, decimal_places=8)),
                ('unconfirmed', models.DecimalField(default=0, verbose_name='Unconfirmed', max_digits=18, decimal_places=8)),
                ('description', models.CharField(max_length=100, null=True, verbose_name='Description', blank=True)),
                ('reason_object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('reason_content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('txid', models.CharField(unique=True, max_length=100, verbose_name='Txid')),
                ('processed', models.BooleanField(default=False, verbose_name='Processed')),
                ('currency', models.ForeignKey(to='cc.Currency')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('balance', models.DecimalField(default=0, verbose_name='Balance', max_digits=18, decimal_places=8)),
                ('holded', models.DecimalField(default=0, verbose_name='Holded', max_digits=18, decimal_places=8)),
                ('unconfirmed', models.DecimalField(default=0, verbose_name='Unconfirmed', max_digits=18, decimal_places=8)),
                ('label', models.CharField(max_length=100, null=True, verbose_name='Label', blank=True)),
                ('currency', models.ForeignKey(to='cc.Currency')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WithdrawTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(verbose_name='Amount', max_digits=18, decimal_places=8)),
                ('address', models.CharField(max_length=50, verbose_name='Address')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created')),
                ('txid', models.CharField(max_length=100, null=True, verbose_name='Txid', blank=True)),
                ('fee', models.DecimalField(null=True, verbose_name='Amount', max_digits=18, decimal_places=8, blank=True)),
                ('currency', models.ForeignKey(to='cc.Currency')),
                ('wallet', models.ForeignKey(to='cc.Wallet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='operation',
            name='wallet',
            field=models.ForeignKey(to='cc.Wallet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='address',
            name='currency',
            field=models.ForeignKey(to='cc.Currency'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='address',
            name='wallet',
            field=models.ForeignKey(related_name=b'addresses', blank=True, to='cc.Wallet', null=True),
            preserve_default=True,
        ),
    ]
