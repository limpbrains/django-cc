# django-cc #


Django-cryptocurrencies web wallet for Bitcoin and other cryptocurrencies.

Simple pluggable application inspired by django-bitcoin.

Python 3

## Features ##
* Multi-currency
* Celery support
* Withdraw and Deposite
* 3 types of balances: balance, unconfirmed, holded

## Quick start ##

Edit Currency model
```python

from cc.models import Currency

currency = Currency.object.create(
    label = 'Bitcoin',
    ticker = 'BTC',
    api_url = 'http://root:toor@localhost:8332'
)
```

Start celery worker
```bash
$ celery worker -A tst.cel.app
```

Get new addresses for wallets

```bash
$ celery call cc.tasks.refill_addresses_queue
```

Now you can create wallets, deposite and withdraw funds

```python

from cc.models import Wallet

wallet = Wallet.objects.create(
    currency=currency
)

wallet.get_address()

wallet.withdraw('mvEnyQ9b9iTA11QMHAwSVtHUrtD4CTfiDB', Decimal('0.01'))
```

After creating a withdraw transaction you need to run

```bash
$ celery call cc.tasks.process_withdraw_transactions
```

Query for new deposite transactions:
```bash
$ cc.tasks.query_transactions
```

If you want to catch event from bitcoind, but these calls options in bitcoin.conf file

```
walletnotify=~/env/bin/celery call cc.tasks.query_transaction --args='["BTC", "'%s'"]'
blocknotify=~/env/bin/celery call cc.tasks.query_transactions --args='["BTC"]'

```
where "BTC" - ticker (short name) of the Currency
