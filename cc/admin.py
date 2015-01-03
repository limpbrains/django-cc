from __future__ import absolute_import

from django.contrib import admin

from . import models
from .forms import WalletAdminForm


class WalletAdmin(admin.ModelAdmin):
    form = WalletAdminForm
    list_display = ('currency', 'balance', 'holded', 'unconfirmed', 'label', 'get_address')
    list_filter = ('currency',)

admin.site.register(models.Wallet, WalletAdmin)


class OperationAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'balance', 'holded', 'unconfirmed', 'description')
    list_filter = ('wallet',)

admin.site.register(models.Operation, OperationAdmin)


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'label', 'last_block')

admin.site.register(models.Currency, CurrencyAdmin)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('txid', 'currency', 'processed')
    list_filter = ('currency', 'processed')

admin.site.register(models.Transaction, TransactionAdmin)


class AddressAdmin(admin.ModelAdmin):
    list_display = ('address', 'currency', 'created', 'active', 'label', 'wallet')
    list_filter = ('currency', 'active')

admin.site.register(models.Address, AddressAdmin)


class WithdrawTransactionAdmin(admin.ModelAdmin):
    list_display = ('currency', 'amount', 'address', 'wallet', 'created', 'txid', 'fee')
    list_filter = ('currency',)

admin.site.register(models.WithdrawTransaction, WithdrawTransactionAdmin)
