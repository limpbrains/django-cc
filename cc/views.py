from __future__ import absolute_import

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.http.request import validate_host, split_domain_port

from . import settings
from .models import Currency
from .tasks import query_transactions, query_transaction


def cc_validate_host(func):
    def validate(request):
        domain, port = split_domain_port(request.META['HTTP_HOST'])
        if not validate_host(domain, settings.CC_ALLOWED_HOSTS):
            return HttpResponseForbidden('forbiden')

        return func(request)

    return validate


def vaidate_currency(func):
    def validate(request):
        ticker = request.GET.get('currency')
        if not ticker:
            return HttpResponseBadRequest('Currency is missing')

        try:
            currency = Currency.objects.get(ticker=ticker)
        except Currency.DoesNotExist:
            return HttpResponseBadRequest('Wrong currency ticker')

        return func(request)

    return validate


def vaidate_txid(func):
    def validate(request):
        if not request.GET.get('txid'):
            return HttpResponseBadRequest('Txid is missing')

        return func(request)

    return validate


@cc_validate_host
@vaidate_currency
def blocknotify(request):
    query_transactions.delay(ticker=request.GET['currency'])
    return HttpResponse('success')


@cc_validate_host
@vaidate_currency
@vaidate_txid
def walletnotify(request):
    query_transaction.delay(request.GET['currency'], request.GET['txid'])
    return HttpResponse('success')
