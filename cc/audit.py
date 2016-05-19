from decimal import Decimal as D

from cc.models import Wallet, Operation, Address, Currency, Transaction, WithdrawTransaction


def total_recieved(ticker, listreceivedbyaddress):
    currency = Currency.objects.get(ticker=ticker)
    wallets = Wallet.objects.filter(currency=currency)

    data = dict(map(lambda x: [x['address'], x['amount']], listreceivedbyaddress))

    result = {'mismatch': [], 'missing': []}

    for w in wallets:
        tr = w.total_received()
        if tr > 0:
            summ = D('0')
            for a in Address.objects.filter(wallet = w):
                try:
                    summ += data[a.address]
                except KeyError:
                    result['missing'].append({'address': a.address})

            if (tr != summ):
                result['mismatch'].append({
                    'wallet': w.id,
                    'db': tr,
                    'coin': summ,
                })

    return result


def double_spend(ticker, listtransactions, ccc):
    currency = Currency.objects.get(ticker=ticker)


    send = filter(lambda x: x['category'] == 'send', listtransactions)
    missing = []

    for tx in send:
        wtxs = WithdrawTransaction.objects.filter(txid=tx['txid'], currency=currency)

        if not wtxs:
            ccc.stdout.write(ccc.style.ERROR('Missing %(txid)s  %(address)s  %(amount)s  %(time)s' % tx))
            missing.append(tx)



    import IPython; IPython.embed()
    return

    return result
