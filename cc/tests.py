import string
import random
from decimal import Decimal
from mock import patch, MagicMock

from django.test import TransactionTestCase

from cc.models import Wallet, Address, Currency, Operation, Transaction, WithdrawTransaction
from cc import tasks
from cc import settings


settings.CC_CONFIRMATIONS = 2
settings.CC_ACCOUNT = ''


class DepositeTransaction(TransactionTestCase):
    def setUp(self):
        self.txdict = {
            'category': 'receive',
            'account': '',
            'blockhash': '000000008468ce0ec51c64aa98cf99b317274c5287e770c9eddaa83fa33222ef',
            'blockindex': 1,
            'walletconflicts': [],
            'time': 1409150845,
            'txid': '63fadb05b2f6b0c83925d402c6cf27bc841acaa8c89a335914f77f75b22ef5dc',
            'blocktime': 1409154118,
            'amount': Decimal('5.00000000'),
            'confirmations': 87,
            'timereceived': 1409150845,
            'address': 'mmxv3wYKozehzp3GZSUiKvRCWSJecWNSrd'
        }
        self.currency = Currency.objects.create(label='Bitcoin', ticker='btc')
        self.wallet = Wallet.objects.create(currency=self.currency, label='Test')
        self.address = Address.objects.create(address=self.txdict['address'], wallet=self.wallet, currency=self.currency)
        tasks.process_deposite_transaction(self.txdict, 'btc')

    def test_balance(self):
        wallet = Wallet.objects.get(id=self.wallet.id)
        self.assertEqual(wallet.balance, self.txdict['amount'])

    def test_tx(self):
        tx = Transaction.objects.get(txid=self.txdict['txid'])
        self.assertTrue(tx.processed)


class UnconfirmedTransaction(TransactionTestCase):
    def setUp(self):
        self.txdict = {
            'category': 'receive',
            'account': '',
            'blockhash': '000000008468ce0ec51c64aa98cf99b317274c5287e770c9eddaa83fa33222ef',
            'blockindex': 1,
            'walletconflicts': [],
            'time': 1409150845,
            'txid': '63fadb05b2f6b0c83925d402c6cf27bc841acaa8c89a335914f77f75b22ef5dc',
            'blocktime': 1409154118,
            'amount': Decimal('5.00000000'),
            'confirmations': 1,
            'timereceived': 1409150845,
            'address': 'mmxv3wYKozehzp3GZSUiKvRCWSJecWNSrd'
        }
        self.currency = Currency.objects.create(label='Bitcoin', ticker='btc')
        self.wallet = Wallet.objects.create(currency=self.currency, label='Test')
        self.address = Address.objects.create(address=self.txdict['address'], wallet=self.wallet, currency=self.currency)
        tasks.process_deposite_transaction(self.txdict, 'btc')

    def test_balance(self):
        wallet = Wallet.objects.get(id=self.wallet.id)
        self.assertEqual(wallet.unconfirmed, self.txdict['amount'])
        self.assertEqual(wallet.balance, Decimal('0'))

    def test_tx(self):
        tx = Transaction.objects.get(txid=self.txdict['txid'])
        self.assertFalse(tx.processed)


class ImmatureTransaction(TransactionTestCase):
    def setUp(self):
        self.txdict = {
            'category': 'immature',
            'account': '',
            'blockhash': '000000008468ce0ec51c64aa98cf99b317274c5287e770c9eddaa83fa33222ef',
            'blockindex': 1,
            'walletconflicts': [],
            'time': 1422794361,
            'txid': '63fadb05b2f6b0c83925d402c6cf27bc841acaa8c89a335914f77f75b22ef5dc',
            'blocktime': 1409154118,
            'amount': Decimal('1.00000000'),
            'confirmations': 1,
            'timereceived': 1422794579,
            'address': '12aJBBXWcWPxfQbXL4PQ3qtx978wwLL2g9'
        }
        self.currency = Currency.objects.create(label='Bitcoin', ticker='btc')
        self.wallet = Wallet.objects.create(currency=self.currency, label='Test')
        self.address = Address.objects.create(address=self.txdict['address'], wallet=self.wallet, currency=self.currency)
        tasks.process_deposite_transaction(self.txdict, 'btc')

    def test_balance(self):
        wallet = Wallet.objects.get(id=self.wallet.id)
        self.assertEqual(wallet.unconfirmed, self.txdict['amount'])
        self.assertEqual(wallet.balance, Decimal('0'))

    def test_tx(self):
        tx = Transaction.objects.get(txid=self.txdict['txid'])
        self.assertFalse(tx.processed)


class ConfirmTransaction(TransactionTestCase):
    def setUp(self):
        self.txdict = {
            'category': 'receive',
            'account': '',
            'blockhash': '000000008468ce0ec51c64aa98cf99b317274c5287e770c9eddaa83fa33222ef',
            'blockindex': 1,
            'walletconflicts': [],
            'time': 1409150845,
            'txid': '63fadb05b2f6b0c83925d402c6cf27bc841acaa8c89a335914f77f75b22ef5dc',
            'blocktime': 1409154118,
            'amount': Decimal('5.00000000'),
            'confirmations': 3,
            'timereceived': 1409150845,
            'address': 'mmxv3wYKozehzp3GZSUiKvRCWSJecWNSrd'
        }
        self.currency = Currency.objects.create(label='Bitcoin', ticker='btc')
        self.wallet = Wallet.objects.create(currency=self.currency, label='Test', unconfirmed=Decimal('5.0'))
        self.address = Address.objects.create(address=self.txdict['address'], wallet=self.wallet, currency=self.currency)
        self.tx = Transaction.objects.create(txid=self.txdict['txid'], address=self.txdict['address'], currency=self.currency)
        tasks.process_deposite_transaction(self.txdict, 'btc')

    def test_balance(self):
        wallet = Wallet.objects.get(id=self.wallet.id)
        self.assertEqual(wallet.balance, Decimal('5.0'))
        self.assertEqual(wallet.unconfirmed, Decimal('0'))

    def test_tx(self):
        tx = Transaction.objects.get(id=self.tx.id)
        self.assertTrue(tx.processed)


class WalletAddress(TransactionTestCase):
    def setUp(self):
        self.btc = Currency.objects.create(label='Bitcoin', ticker='btc')
        self.ltc = Currency.objects.create(label='Litecoin', ticker='ltc', magicbyte='48')
        self.wallet = Wallet.objects.create(currency=self.btc, label='Test')

    def test_no_addresses(self):
        self.assertIsNone(self.wallet.get_address())

    def test_active_address(self):
        active = Address.objects.create(address='1111111111111111111114oLvT2', wallet=self.wallet, currency=self.btc, active=True)
        Address.objects.create(address='1AGNa15ZQXAZUgFiqJ2i7Z2DPU2J6hW62i', wallet=self.wallet, currency=self.btc, active=False)
        self.assertEqual(self.wallet.get_address(), active)

    def test_unused_address(self):
        unused = Address.objects.create(address='1Eym7pyJcaambv8FG4ZoU8A4xsiL9us2zz', wallet=self.wallet, currency=self.btc, active=False)
        Address.objects.create(address='LRNYxwQsHpm2A1VhawrJQti3nUkPN7vtq3', currency=self.ltc, active=True)
        self.assertEqual(self.wallet.get_address(), unused)


class WalletWithdraw(TransactionTestCase):
    def setUp(self):
        self.btc = Currency.objects.create(label='Bitcoin', ticker='btc')
        self.wallet = Wallet.objects.create(currency=self.btc, label='Test', balance=Decimal('1.0'))
        self.amount = Decimal('1.0')
        self.address = '1111111111111111111114oLvT2'
        self.desc = 'some desc'

    def test_operation(self):
        self.wallet.withdraw_to_address(self.address, self.amount, self.desc)
        op = Operation.objects.all()[0]

        self.assertEqual(op.wallet, self.wallet)
        self.assertEqual(op.holded, self.amount)
        self.assertEqual(op.balance, -self.amount)
        self.assertEqual(op.description, self.desc)
        self.assertIsNotNone(op.reason)

    def test_wallet(self):
        self.wallet.withdraw_to_address(self.address, self.amount, self.desc)
        wallet = Wallet.objects.get(id=self.wallet.id)
        self.assertEqual(wallet.balance, Decimal('0'))
        self.assertEqual(wallet.holded, self.amount)

    def test_no_money(self):
        with self.assertRaises(ValueError):
            self.wallet.withdraw_to_address(self.address, Decimal('100'))

    def test_wrong_address(self):
        with self.assertRaises(ValueError):
            self.wallet.withdraw_to_address('mz4ZbfKfU4SQWRDagkfX2TLAotpimAAVFE', Decimal('100'))


class TaskWithdraw(TransactionTestCase):
    def setUp(self):
        self.currency = Currency.objects.create(label='Testnet', ticker='tst', magicbyte='111,196')
        self.wallet = Wallet.objects.create(currency=self.currency, label='Test', balance=Decimal('1.0'))
        self.txid = 'ea12fb225a0665e6ca35ab3fd7a514c36d1d5028d99340931d745dab62c13f8a'

        self.mock = MagicMock(name='asp')
        self.mock.return_value = self.mock
        self.mock.sendmany.return_value = self.txid
        self.mock.gettransaction.return_value = {
            'fee': Decimal('-0.00010000'),
            'timereceived': 1410086093,
            'hex': '010000000181d61f31536c155f43149bfa1a1ed0cd45c504f82e27f8411f14e6b37f926c62000000006a47304402206ac1b06a2ab1ad05c7874728188c73d99de7b8185bda0bce28e06762ea265ec0022050e614fe7aa4d34b75e6465685f12e3589a34763afa383414aaf4d2d62171ba20121020e871b50e2e1d46cac2f2b7611f1fcc97d41e9ced660682191c6ea391c7189e5ffffffff04e0247c38000000001976a91462403a00c6e4906d7624818eae2dc7572f0f592588ac002d3101000000001976a914a17b7337c17ab511686649515f7861944035846588ac80969800000000001976a91437138adaa16d895739a61d10d33fd0b898db552288ac80969800000000001976a914a621b489961d24092eba3838d3142173a8f9d8c488ac00000000',
            'txid': 'ea12fb225a0665e6ca35ab3fd7a514c36d1d5028d99340931d745dab62c13f8a',
            'amount': Decimal('-0.40000000'),
            'walletconflicts': [],
            'details': [{'category': 'send',
            'account': '',
            'fee': Decimal('-0.00010000'),
            'amount': Decimal('-0.20000000'),
            'address': 'mvEnyQ9b9iTA11QMHAwSVtHUrtD4CTfiDB'},
            {'category': 'send',
            'account': '',
            'fee': Decimal('-0.00010000'),
            'amount': Decimal('-0.10000000'),
            'address': 'mkYAsS9QLYo5mXVjuvxKkZUhQJxiMLX5Xk'},
            {'category': 'send',
            'account': '',
            'fee': Decimal('-0.00010000'),
            'amount': Decimal('-0.10000000'),
            'address': 'mvfNqn5AoVWrsJGuKrdPuoQhYs71CR9uFA'}],
            'confirmations': 0,
            'time': 1410086093
        }


    def test_process_withdraw_transactions(self):
        self.wallet.withdraw_to_address('mvEnyQ9b9iTA11QMHAwSVtHUrtD4CTfiDB', Decimal('0.1'))
        self.wallet.withdraw_to_address('mkYAsS9QLYo5mXVjuvxKkZUhQJxiMLX5Xk', Decimal('0.1'))
        self.wallet.withdraw_to_address('mvEnyQ9b9iTA11QMHAwSVtHUrtD4CTfiDB', Decimal('0.1'))
        self.wallet.withdraw_to_address('mvfNqn5AoVWrsJGuKrdPuoQhYs71CR9uFA', Decimal('0.1'))

        with patch('cc.tasks.AuthServiceProxy', self.mock):
            tasks.process_withdraw_transactions(ticker=self.currency.ticker)

        self.mock.gettransaction.assert_called_once_with(self.txid)
        self.mock.sendmany.assert_called_once_with('', {
            'mvEnyQ9b9iTA11QMHAwSVtHUrtD4CTfiDB': Decimal('0.2'),
            'mkYAsS9QLYo5mXVjuvxKkZUhQJxiMLX5Xk': Decimal('0.1'),
            'mvfNqn5AoVWrsJGuKrdPuoQhYs71CR9uFA': Decimal('0.1')
        })

        wallet = Wallet.objects.get(id=self.wallet.id)
        self.assertEqual(wallet.holded, Decimal('0'))
        self.assertEqual(wallet.balance, Decimal('0.5999'))

        fee_operation = Operation.objects.get(wallet=wallet, description='Network fee')
        self.assertEqual(fee_operation.balance, Decimal('-0.0001'))
        self.assertEqual(fee_operation.holded, Decimal('-0.4'))


class TaskRefillAddressQueue(TransactionTestCase):
    def setUp(self):
        self.currency = Currency.objects.create(label='Testnet', ticker='tst', magicbyte='111,196')
        self.wallet = Wallet.objects.create(currency=self.currency)

        self.mock = MagicMock(name='asp')
        self.mock.return_value = self.mock
        self.mock.getnewaddress.side_effect = lambda: ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))

    def refill_addresses_queue(self):
        self.assertEqual(len(Address.objects.all()), 0)

        with patch('cc.tasks.AuthServiceProxy', self.mock):
            tasks.refill_addresses_queue()

        self.assertEqual(len(Address.objects.all()), settings.CC_ADDRESS_QUEUE)


class WalletTransfer(TransactionTestCase):
    def setUp(self):
        self.currency = Currency.objects.create(label='Testnet', ticker='tst', magicbyte='111,196')
        self.wallet1 = Wallet.objects.create(currency=self.currency, balance=1)
        self.wallet2 = Wallet.objects.create(currency=self.currency, balance=0)

    def test_transfer(self):
        self.wallet1.transfer(Decimal('1'), self.wallet2)

        self.assertEqual(self.wallet1.balance, 0)
        self.assertEqual(self.wallet2.balance, 1)

        o1 = Operation.objects.get(wallet=self.wallet1)
        o2 = Operation.objects.get(wallet=self.wallet2)

        self.assertEqual(o1.balance, -1)
        self.assertEqual(o2.balance, 1)


class QueryTransaction(TransactionTestCase):
    def setUp(self):
        self.txdict = {
            "amount" : Decimal('3'),
            "confirmations" : 54271,
            "blockhash" : "00000000000000017adae0a02c36e7a6379991aad2ce35c2ba1b540aff01d7b8",
            "blockindex" : 744,
            "blocktime" : 1391222639,
            "txid" : "01c17411ff6a4278ada87c28dad74b9d1e79c799743fd2d63dac945645123ab3",
            "walletconflicts" : [
            ],
            "time" : 1391222405,
            "timereceived" : 1391222405,
            "details" : [
                {
                    "account" : "somerandomstring14aqqwd",
                    "address" : "16ahqjUA7VJMuBpKjR3zX48xnTgPMM47cr",
                    "category" : "receive",
                    "amount" : Decimal('1')
                },
                {
                    "account" : "somerandomstring14aqqwd",
                    "address" : "1FLrCWUJw5SG7uDHzkrRLih55PxMC763eu",
                    "category" : "receive",
                    "amount" : Decimal('2')
                }
            ]
        }
        self.currency = Currency.objects.create(label='BItcoin', ticker='BTC', magicbyte='0,5')
        self.wallet = Wallet.objects.create(currency=self.currency, label='Test')
        self.address1 = Address.objects.create(address=self.txdict['details'][0]['address'], wallet=self.wallet, currency=self.currency)
        self.address2 = Address.objects.create(address=self.txdict['details'][1]['address'], wallet=self.wallet, currency=self.currency)

        self.mock = MagicMock(name='asp')
        self.mock.return_value = self.mock
        self.mock.gettransaction.return_value = self.txdict

    def test_balance(self):
        with patch('cc.tasks.AuthServiceProxy', self.mock):
            tasks.query_transaction('BTC', self.txdict['txid'])

        wallet = Wallet.objects.get(id=self.wallet.id)

        self.assertEqual(wallet.balance, Decimal('3'))


class Dust(TransactionTestCase):
    def setUp(self):
        self.currency = Currency.objects.create(label='Testnet', ticker='tst', magicbyte='111,196', dust=Decimal('0.00005430'))
        self.wallet = Wallet.objects.create(currency=self.currency, label='Test', balance=Decimal('2.0'))
        self.txid = 'ea12fb225a0665e6ca35ab3fd7a514c36d1d5028d99340931d745dab62c13f8a'

        self.mock = MagicMock(name='asp')
        self.mock.return_value = self.mock
        self.mock.sendmany.return_value = self.txid
        self.mock.gettransaction.return_value = {
            'fee': Decimal('-0.00010000'),
            'timereceived': 1410086093,
            'hex': '010000000181d61f31536c155f43149bfa1a1ed0cd45c504f82e27f8411f14e6b37f926c62000000006a47304402206ac1b06a2ab1ad05c7874728188c73d99de7b8185bda0bce28e06762ea265ec0022050e614fe7aa4d34b75e6465685f12e3589a34763afa383414aaf4d2d62171ba20121020e871b50e2e1d46cac2f2b7611f1fcc97d41e9ced660682191c6ea391c7189e5ffffffff04e0247c38000000001976a91462403a00c6e4906d7624818eae2dc7572f0f592588ac002d3101000000001976a914a17b7337c17ab511686649515f7861944035846588ac80969800000000001976a91437138adaa16d895739a61d10d33fd0b898db552288ac80969800000000001976a914a621b489961d24092eba3838d3142173a8f9d8c488ac00000000',
            'txid': 'ea12fb225a0665e6ca35ab3fd7a514c36d1d5028d99340931d745dab62c13f8a',
            'amount': Decimal('-10000000'),
            'walletconflicts': [],
            'details': [{'category': 'send',
            'account': '',
            'fee': Decimal('-0.00010000'),
            'amount': Decimal('-1.0000000'),
            'address': 'mvEnyQ9b9iTA11QMHAwSVtHUrtD4CTfiDB'}]
        }

    def test_process_withdraw_transactions(self):
        self.wallet.withdraw_to_address('mvEnyQ9b9iTA11QMHAwSVtHUrtD4CTfiDB', Decimal('1'))
        self.wallet.withdraw_to_address('mvfNqn5AoVWrsJGuKrdPuoQhYs71CR9uFA', Decimal('0.00000001'))

        with patch('cc.tasks.AuthServiceProxy', self.mock):
            tasks.process_withdraw_transactions(ticker=self.currency.ticker)

        self.mock.sendmany.assert_called_once_with('', {
            'mvEnyQ9b9iTA11QMHAwSVtHUrtD4CTfiDB': Decimal('1')
        })

        wallet = Wallet.objects.get(id=self.wallet.id)
        self.assertEqual(wallet.balance, Decimal('0.99989999'))

        wt1 = WithdrawTransaction.objects.get(address='mvEnyQ9b9iTA11QMHAwSVtHUrtD4CTfiDB')
        wt2 = WithdrawTransaction.objects.get(address='mvfNqn5AoVWrsJGuKrdPuoQhYs71CR9uFA')
        self.assertEqual(wt1.txid, self.txid)
        self.assertIsNone(wt2.txid)
