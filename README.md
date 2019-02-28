# django-cc #
[![Build Status](https://travis-ci.org/limpbrains/django-cc.svg?branch=master)](https://travis-ci.org/limpbrains/django-cc)

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

currency = Currency.objects.create(
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

wallet.withdraw_to_address('mvEnyQ9b9iTA11QMHAwSVtHUrtD4CTfiDB', Decimal('0.01'))
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

### Transactions

When you write applications that are working with money it is extremely important to use Database transactions. Currenly django-cc doesn't inclues any `@transaction.atomic`. You should do this by yourself.

In my code I have a higher level wrapper with @transaction.atomic and to get wallets I'm always using select for update, like `Wallet.objects.select_for_update().get(addresses=address)` to get a lock over the Wallet.

## Supported crypto currencies

In general django-cc should work with most Bitcoin forks. I've tested it against: Bitcoin, Litecoin, Zcash (not anonymous transactions), Dogecoin and Dash. 

When you are adding any other `Currency`, than Bitcoin, you should define `magicbyte` and `dust` values. Use tables below to get the values.

### Magic bytes

Magic bytes are used to verify withdraw addresses. They are different for each cryptocurrency

| CC       | Mainnet | Testnet |
| -------- | ------- | ------- |
| Bitcoin  | 0,5     | 111,196 | 
| Litecoin | 48,50   | 58      | 
| Zcash    | 28      | 29      | 
| Dogecoin | 30,22   |         | 
| Dash     | 76,16   | 140     | 

### Dust

Minimal amount of valid transaction

| CC       | Dust size    |
| -------- | ------------ |
| Bitcoin  | `0.00005430` |
| Litecoin | `0.00054600` |

### Testing

Tests are written using Regtest. To run them you need docker and docker-compose. Simply run `docker-compose up` and it will build and run all tests for you. Usually it takes about 5 min to run all the tests.
