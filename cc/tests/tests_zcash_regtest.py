import string
import random
from time import sleep
from decimal import Decimal
from mock import patch, MagicMock
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from django.test import TransactionTestCase

from cc.models import Wallet, Address, Currency, Operation, Transaction, WithdrawTransaction
from cc import tasks
from cc import settings


settings.CC_CONFIRMATIONS = 2
settings.CC_ACCOUNT = ''
URL = 'http://root:toor@zcashd:18232/'


class WalletAddressGet(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.coin = AuthServiceProxy(URL)
        starting = True
        while starting:
            try:
                cls.coin.generate(101)
            except JSONRPCException as e:
                if e.code != -28:
                    raise
            else:
                starting = False
                sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.coin.stop()
        super().tearDownClass()

    def setUp(self):
        self.currency = Currency.objects.create(label='Zcash regtest', ticker='tzec', api_url=URL, magicbyte='29')
        tasks.refill_addresses_queue()

    def wait_for_operation(self, operation):
        waiting = True
        while waiting:
            waiting = self.coin.z_getoperationstatus([operation])[0]['status'] != 'success'
            sleep(1)

    def test_address_refill(self):
        wallet = Wallet.objects.create(currency=self.currency)
        address = wallet.get_address()
        self.assertTrue(address)

    def test_deposit(self):
        wallet_before = Wallet.objects.create(currency=self.currency)
        address = wallet_before.get_address().address
        self.coin.sendtoaddress(address, Decimal('1'))
        self.coin.generate(1)

        tasks.query_transactions('tzec')
        wallet_after1 = Wallet.objects.get(id=wallet_before.id)
        self.assertEqual(wallet_after1.balance, Decimal('0'))
        self.assertEqual(wallet_after1.holded, Decimal('0'))
        self.assertEqual(wallet_after1.unconfirmed, Decimal('1'))
        self.coin.generate(1)

        tasks.query_transactions('tzec')
        wallet_after2 = Wallet.objects.get(id=wallet_before.id)
        self.assertEqual(wallet_after2.balance, Decimal('1'))
        self.assertEqual(wallet_after2.holded, Decimal('0'))
        self.assertEqual(wallet_after2.unconfirmed, Decimal('0'))

    def test_withdraw(self):
        wallet_before = Wallet.objects.create(currency=self.currency, balance=Decimal('1.0'))
        wallet_before.withdraw_to_address('tmGa4dwQrtw6ctnijug586PwXt9h8JExguc', Decimal('0.1'))
        wallet_before.withdraw_to_address('tmEHsxHvPS5inmcDYPDocFPmynGCz5PLYf3', Decimal('0.1'))
        wallet_before.withdraw_to_address('tmGa4dwQrtw6ctnijug586PwXt9h8JExguc', Decimal('0.1'))

        wallet_after1 = Wallet.objects.get(id=wallet_before.id)
        self.assertEqual(wallet_after1.balance, Decimal('0.7'))
        self.assertEqual(wallet_after1.holded, Decimal('0.3'))
        tasks.process_withdraw_transactions('tzec')
        self.coin.generate(2)

        wtx = WithdrawTransaction.objects.last()
        tx = self.coin.gettransaction(wtx.txid)

        wallet_after2 = Wallet.objects.get(id=wallet_before.id)
        self.assertEqual(wallet_after2.balance, Decimal('0.7') + tx['fee'])
        self.assertEqual(wallet_after2.holded, Decimal('0'))

    def test_withdraw_error(self):
        wallet_before = Wallet.objects.create(currency=self.currency, balance=Decimal('21000000'))
        wallet_before.withdraw_to_address('tmGa4dwQrtw6ctnijug586PwXt9h8JExguc', Decimal('21000000'))

        try:
            tasks.process_withdraw_transactions('tzec')
        except JSONRPCException:
            pass

        wallet_after1 = Wallet.objects.get(id=wallet_before.id)
        self.assertEqual(wallet_after1.balance, Decimal('0'))
        self.assertEqual(wallet_after1.holded, Decimal('21000000'))

        wtx = WithdrawTransaction.objects.last()

        wallet_after1 = Wallet.objects.get(id=wallet_before.id)
        self.assertEqual(wtx.state, wtx.ERROR)

    def test_deposit_from_z(self):
        zaddress = self.coin.z_getnewaddress('sprout')
        unspent = [u for u in self.coin.listunspent() if u['amount'] > 6][0]
        amount = unspent['amount']
        operation1 = self.coin.z_sendmany(unspent['address'], [{'address': zaddress, 'amount': amount}], 1, 0)
        self.wait_for_operation(operation1)
        self.coin.generate(6)

        wallet_before = Wallet.objects.create(currency=self.currency)
        address = wallet_before.get_address().address
        operation2 = self.coin.z_sendmany(zaddress, [{'address': address, "amount": amount}], 1, 0)
        self.wait_for_operation(operation2)
        self.coin.generate(1)

        tasks.query_transactions('tzec')
        wallet_after1 = Wallet.objects.get(id=wallet_before.id)
        self.assertEqual(wallet_after1.balance, Decimal('0'))
        self.assertEqual(wallet_after1.holded, Decimal('0'))
        self.assertGreaterEqual(wallet_after1.unconfirmed, amount) # FIXME should be assertEqual
        self.coin.generate(1)

        tasks.query_transactions('tzec')
        wallet_after2 = Wallet.objects.get(id=wallet_before.id)
        self.assertEqual(wallet_after2.balance, amount)
        self.assertEqual(wallet_after2.holded, Decimal('0'))
        self.assertGreaterEqual(wallet_after2.unconfirmed, Decimal('0')) # FIXME should be assertEqual
