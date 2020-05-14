# django-cc #
[![Build Status](https://travis-ci.org/limpbrains/django-cc.svg?branch=master)](https://travis-ci.org/limpbrains/django-cc)

Django-cryptocurrencies web wallet for Bitcoin and a few other cryptocurrencies.

Simple pluggable application inspired by django-bitcoin.

Python 3

## Features ##
* Multi-currency
* Celery support
* Withdraw and Deposit
* 3 types of balances: balance, unconfirmed, holded
* Works over bitcoind json-rpc

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

Start Celery worker
```bash
$ celery worker -A tst.cel.app
```

Get new addresses for wallets

```bash
$ celery call cc.tasks.refill_addresses_queue
```

Now you can create wallets, deposit and withdraw funds

```python
from cc.models import Wallet

wallet = Wallet.objects.create(
    currency=currency
)

wallet.get_address()

wallet.withdraw_to_address('mvEnyQ9b9iTA11QMHAwSVtHUrtD4CTfiDB', Decimal('0.01'))
```

After creating a withdraw transaction, you need to run

```bash
$ celery call cc.tasks.process_withdraw_transactions
```

Query for new deposit transactions:
```bash
$ cc.tasks.query_transactions
```

If you want to catch event from bitcoind, but these calls options in bitcoin.conf file

```
walletnotify=~/env/bin/celery call cc.tasks.query_transaction --args='["BTC", "'%s'"]'
blocknotify=~/env/bin/celery call cc.tasks.query_transactions --args='["BTC"]'
```
where "BTC" - ticker (short name) of the Currency

## More details

### Limitations ###
* Works with full node. For each cryptocurrency you will need to run a full node, which usually requires a lot of disk space. But by running full node you are actually helping the network, so it is a good thing.
* Coins are mixed between wallets. When you withdraw funds from the wallet, you can't choose which UTXO will be used.
* During the withdrawal you can't choose transaction fee. 'Django-cc' uses 'send_many' RPC call, bitcoind calculates how much you will spend on transaction fee. When withdraw is finished, spent fee will be subtracted from wallet balance. To reduce fees, change 'txconfirmtarget' in your bitcoin.conf.

### Configuring Celery tasks ###
This library relies heavily on Celery for running tasks in the background. You need to add it to your Project. There are a few tasks which djano-cc should do periodically:

* 'refill_addresses_queue'. It queries bitcoind for new addresses and store them in DB. Each time you create a wallet and call 'wallet.get_address()' unused address will be attached to the wallet. By default, it keeps amount for new addresses to 20. You can tune this by changing 'CC_ADDRESS_QUEUE' in your project settings. Usually running this task once in an hour is enought.
* 'process_withdraw_transactions'. It queries DB for any new withdraw transactions and executes them. By running it not so often, you can batch transactions, this will help you reduce network fees.
* 'query-transactions'. It queries bitcoind for new incoming transactions and updates wallets balances. Bitcoin network creates one block per approximately 10 minutes, so no need to run it more often.

But it is better to run 'query-transactions' in response to new events from bitcoind. You can do this by adding these lines to bitcoin.conf
```
walletnotify=~/env/bin/celery call cc.tasks.query_transaction --args='["BTC", "'%s'"]'
blocknotify=~/env/bin/celery call cc.tasks.query_transactions --args='["BTC"]'
```
Each time bitcoin will receive new tx or block, you will get an instant update on balances.

If bitcoind works in another environment, you can send this events by HTTP hooks. Expose 'django-cc' views in urls.py:
```python
urlpatterns = [
...
url(r'^cc/', include('cc.urls')),
]
```
Then you can send http requests to trigger actions:
```bash
curl -k "https://yourhost/cc/blocknotify/?currency=BTC"
curl -k "https://yourhost/cc/walletnotify/?currency=BTC&txid=$1"
```

### API ###

Withdraw to network:
```python
wallet.withdraw_to_address('mvEnyQ9b9iTA11QMHAwSVtHUrtD4CTfiDB', Decimal('0.01'))
```

Transfer from wallet to wallet:
```python
wallet1.transfer(wallet1.balance, wallet2, None, 'description')
```

Get wallet history:
```python
for operation in wallet.get_operations():
    print(operation.created)
    print(operation.balance)
    print(operation.reason.txid)
    print(operation.reason.address)
```

### Database transactions

When you write applications that are working with money, it is extremely important to use Database transactions. Currenly django-cc doesn't inclues any '@transaction.atomic'. You should do this by yourself.

In my code I have a higher level wrapper with @transaction.atomic and to get wallets I'm always using select for update, like 'Wallet.objects.select_for_update().get(addresses=address)' to get a lock over the Wallet.

## Supported cryptocurrencies

In general django-cc should work with most Bitcoin forks. I've tested it against: Bitcoin, Litecoin, Zcash (not anonymous transactions), Dogecoin and Dash. 

When you are adding any other than Bitcoin `Currency`, you should define `magicbyte` and `dust` values. Use tables below to get the values.

### Magic bytes

Magic bytes are used to verify withdraw addresses. They are different for each cryptocurrency.

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

### Settings ###

CC_CONFIRMATIONS - how many confirmations incoming transaction needs to increase wallet balance. Default is 2.
CC_ADDRESS_QUEUE - how many addresses generate during `refill_addresses_queue`. Default is 20.
CC_ALLOW_NEGATIVE_BALANCE - minimal amount of Wallet to be able to withdraw funds from it. Default is Decimal('0.001').
CC_ACCOUNT - Bitcoind once had an account system. Now it is deprecated. Do not change this.  Default is '' — empty string.
CC_ALLOWED_HOSTS - list of addresses how can call `/cc/blocknotify` and `/cc/walletnotify`. Default is `['localhost', '127.0.0.1']`.

### Testing

Tests are written using Regtest. To run them you need docker and docker-compose. Simply run `docker-compose up` and it will build and run all tests for you. Usually it takes about 5 min to run all the tests.
