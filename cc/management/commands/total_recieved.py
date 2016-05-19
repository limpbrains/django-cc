import json
import decimal
import argparse
from django.core.management.base import BaseCommand, CommandError

from cc.audit import total_recieved


class Command(BaseCommand):
    help = 'Checks total recieved with output of "listreceivedbyaddress" bitcoind command'

    def add_arguments(self, parser):
        parser.add_argument('ticker', type=str)
        parser.add_argument('file', type=argparse.FileType('r'))

    def handle(self, *args, **options):
        data = json.load(options['file'], parse_float=decimal.Decimal)
        result = total_recieved(options['ticker'], data)

        if not result['mismatch'] and not result['missing']:
            self.stdout.write(self.style.SUCCESS('Everything is allright'))

        elif result['mismatch']:
            for m in result['mismatch']:
                self.stdout.write(self.style.ERROR('Wallet: "%(wallet)s" balance mismatch DB: %(db)s WALLET: %(coin)s' % m))

        elif result['missing']:
            for m in result['missing']:
                self.stdout.write(self.style.ERROR('Address "%(address)s" is missing' % m))

        return
