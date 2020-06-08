import getopt
import csv
import sys

import arrow
from ofxparse import Statement, Transaction, Account
from ofxparse import OfxPrinter
from ofxparse.ofxparse import Ofx


class AccountTransactionBuilder(object):
    def __init__(self, account_id):
        self.account = Account()
        self.account.account_id = account_id
        self.account.statement = Statement()
        self.account.statement.available_balance = None
        self.account.statement.available_balance_date = None
        self.account.statement.balance = None
        self.account.statement.balance_date = None

        self.date_transaction_counters = {}

    def _get_and_increment_transaction_counter(self, date_string):
        if date_string not in self.date_transaction_counters:
            self.date_transaction_counters[date_string] = 1
        counter = self.date_transaction_counters[date_string]
        self.date_transaction_counters[date_string] = counter + 1
        return counter

    def add_transaction_from_row(self, row):
        #       0          2      4             5       6
        # posted,,05/28/2020,,PAYEE,BankTransType,--21.73
        # note that deposits are double-negative
        transaction = Transaction()
        if row[6].startswith("--"):
            # deposit
            transaction.amount = float(row[6][2:])
        else:
            transaction.amount = float(row[6])
        transaction.date = convert_csv_date_to_ofx_date(row[2])
        self.adjust_start_end_dates(transaction.date)
        # transaction id is prepended with the date, and then a uniqueness counter per day for that account
        transaction.id = "{}120000".format(transaction.date.format("YYYYMMDD")) + str(self._get_and_increment_transaction_counter(transaction.date)).zfill(7)
        transaction.payee = row[4]
        self.account.statement.transactions.append(transaction)

    def adjust_start_end_dates(self, date):
        if not self.account.statement.start_date:
            self.account.statement.start_date = date
        if not self.account.statement.end_date:
            self.account.statement.end_date = date
        if date < self.account.statement.start_date:
            self.account.statement.start_date = date
        if date > self.account.statement.end_date:
            self.account.statement.end_date = date

def convert_csv_date_to_ofx_date(csv_date_string):
    date = arrow.get(csv_date_string, "MM/DD/YYYY")
    return date

def get_transactions_from_named_directory(name, account_id, parse_directory):
    account_transaction_builder = AccountTransactionBuilder(account_id)

    # I just hard-coded this path for my own use, since it'll rarely change.  You may want to insert your
    # root directory here if you're not just running this from an ide.
    file_path = "{}/{}/bk_download.csv".format(parse_directory, name)
    try:
        with open(file_path, 'rb') as csvfile:
            account_map_reader = csv.reader(csvfile, delimiter=',',skipinitialspace=True)
            for row in account_map_reader:
                if len(row) != 7:
                    continue
                if not row[0] == 'posted':
                    continue
                account_transaction_builder.add_transaction_from_row(row)
    except IOError as e:
        print "Failed to find file named '{}'".format(file_path)
        print e
    return account_transaction_builder.account


def main(argv):
    opts, _ = getopt.getopt(argv, "d:")
    parse_directory = None
    print opts
    for opt, arg in opts:
        if opt == '-d':
            parse_directory = arg
    print "parsing {}".format(parse_directory)
    statement = Statement()
    names_to_accounts = get_directories_to_accounts()
    print names_to_accounts
    ofx = Ofx()
    ofx.accounts = []
    ofx.headers = {}
    ofx.signon = None
    ofx.trnuid = 0
    ofx.status = {
        "code": 0,
        "severity": "INFO",
    }
    for name, account_id in names_to_accounts.iteritems():
        account_transactions = get_transactions_from_named_directory(name, account_id, parse_directory)
        if len(account_transactions.statement.transactions) > 0:
            ofx.accounts.append(account_transactions)
        else:
            print "Did not find any transactions for {}".format(name)

    printer = OfxPrinter(ofx, "testing.ofx")
    printer.write()

def get_directories_to_accounts():
    names_to_accounts = {}
    with open('account_maps.csv', 'rb') as csvfile:
        account_map_reader = csv.reader(csvfile, delimiter=',',skipinitialspace=True)
        for row in account_map_reader:
            if row[0].startswith("#"):
                continue
            names_to_accounts[row[1]]=row[0]

    return names_to_accounts

if __name__ == "__main__":
    main(sys.argv[1:])
