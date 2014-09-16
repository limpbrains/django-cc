from __future__ import absolute_import
from socket import error as socket_error
from decimal import Decimal

from celery import shared_task
from celery.utils.log import get_task_logger
from bitcoinrpc.authproxy import AuthServiceProxy

from django.db import transaction

from cc.models import (Wallet, Currency, Transaction, Address,
                       WithdrawTransaction, Operation)
from cc import settings

logger = get_task_logger(__name__)


@shared_task(throws=(socket_error,))
@transaction.atomic
def query_transactions(ticker=None):
    if not ticker:
        for c in Currency.objects.all():
            query_transactions.delay(c.ticker)
        return

    currency = Currency.objects.select_for_update().get(ticker=ticker)
    coin = AuthServiceProxy(currency.api_url)
    current_block = coin.getblockcount()
    processed_transactions = []

    block_hash = coin.getblockhash(currency.last_block)
    transactions = coin.listsinceblock(block_hash)['transactions']

    for tx in transactions:
        if tx['txid'] in processed_transactions:
            continue

        if tx['category'] not in ('receive', 'generated'):
            continue

        process_deposite_transaction(tx, ticker)
        processed_transactions.append(tx['txid'])

    currency.last_block = current_block
    currency.save()

    for tx in Transaction.objects.filter(processed=False, currency=currency):
        query_transaction(ticker, tx.txid)


@transaction.atomic
def process_deposite_transaction(txdict, ticker):
    if txdict['category'] not in ('receive', 'generated'):
        return

    try:
        address = Address.objects.select_for_update().get(address=txdict['address'])
    except Address.DoesNotExist:
        return

    currency = Currency.objects.get(ticker=ticker)

    try:
        wallet = Wallet.objects.select_for_update().get(addresses=address)
    except Wallet.DoesNotExist:
        wallet, created = Wallet.objects.select_for_update().get_or_create(
            currency=currency,
            label='_unknown_wallet'
        )
        address.wallet = wallet
        address.save()

    tx, created = Transaction.objects.select_for_update().get_or_create(txid=txdict['txid'], currency=currency)

    if tx.processed:
        return

    if created:
        if txdict['confirmations'] >= settings.CC_CONFIRMATIONS:
            Operation.objects.create(
                wallet=wallet,
                balance=txdict['amount'],
                description='Deposite',
                reason=tx
            )
            wallet.balance += txdict['amount']
            wallet.save()
            tx.processed = True
        else:
            Operation.objects.create(
                wallet=wallet,
                unconfirmed=txdict['amount'],
                description='Unconfirmed',
                reason=tx
            )
            wallet.unconfirmed += txdict['amount']
            wallet.save()

    else:
        if txdict['confirmations'] >= settings.CC_CONFIRMATIONS:
            Operation.objects.create(
                wallet=wallet,
                unconfirmed=-txdict['amount'],
                balance=txdict['amount'],
                description='Confirmed',
                reason=tx
            )
            wallet.unconfirmed -= txdict['amount']
            wallet.balance += txdict['amount']
            wallet.save()
            tx.processed = True

    tx.save()


@shared_task(throws=(socket_error,))
@transaction.atomic
def query_transaction(ticker, txid):
    currency = Currency.objects.select_for_update().get(ticker=ticker)
    coin = AuthServiceProxy(currency.api_url)
    txdict = normalise_txifno(coin.gettransaction(txid))
    process_deposite_transaction(txdict, ticker)


def normalise_txifno(data):
    txdict = data['details'][0]
    txdict['confirmations'] = data['confirmations']
    txdict['txid'] = data['txid']
    txdict['timereceived'] = data['timereceived']
    txdict['time'] = data['time']
    return txdict


@shared_task(throws=(socket_error,))
@transaction.atomic
def refill_addresses_queue():
    for currency in Currency.objects.all():
        coin = AuthServiceProxy(currency.api_url)
        count = Address.objects.filter(currency=currency, active=True, wallet=None).count()

        if count < settings.CC_ADDRESS_QUEUE:
            for i in xrange(count, settings.CC_ADDRESS_QUEUE):
                Address.objects.create(address=coin.getnewaddress(), currency=currency)


@shared_task(throws=(socket_error,))
@transaction.atomic
def process_withdraw_transacions(ticker=None):
    if not ticker:
        for c in Currency.objects.all():
            process_withdraw_transacions.delay(c.ticker)
        return

    currency = Currency.objects.select_for_update().get(ticker=ticker)
    coin = AuthServiceProxy(currency.api_url)

    wtxs = WithdrawTransaction.objects.select_for_update().select_related('wallet').filter(currency=currency, txid=None)

    transaction_hash = {}
    for tx in wtxs:
        if tx.address in transaction_hash:
            transaction_hash[tx.address] += tx.amount
        else:
            transaction_hash[tx.address] = tx.amount
    if not transaction_hash:
        return

    txid = coin.sendmany("", transaction_hash)

    if not txid:
        return

    fee = coin.gettransaction(txid).get('fee', 0) * -1
    if not fee:
        fee_per_tx = 0
    else:
        fee_per_tx = (fee / len(wtxs)).quantize(Decimal("0.00000001"))

    for tx in wtxs:
        Operation.objects.create(
            wallet=tx.wallet,
            holded=-tx.amount,
            balance=-fee_per_tx,
            description='Withdraw',
            reason=tx
        )

        wallet = Wallet.objects.get(id=tx.wallet.id)
        wallet.balance -= fee_per_tx
        wallet.holded -= tx.amount
        wallet.save()

    wtxs.update(txid=txid, fee=fee_per_tx)
