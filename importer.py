from beancount.ingest import importer
from beancount.core.amount import Amount, Decimal
import beancount.ingest.extract
from beancount.core import data
from enum import Enum
from datetime import datetime
import csv
from config import BANK_CARD

beancount.ingest.extract.HEADER = ''


PAYEE = "中国科学技术大学"


class Assets(Enum):
    FIXME = "Assets:FIXME"


class Description(Enum):
    CONSUMPTION = "消费"
    CHARGE = "圈存机充值"
    SUBSIDIES = "主机补助"


class USTCCardImporter(importer.ImporterProtocol):
    def __init__(self, account, bank, category):
        self.account = account
        self.bank = bank
        self.category = category

    def identify(self, file):
        """Return true if this importer matches the given file.

        Args:
          file: A cache.FileMemo instance.
        Returns:
          A boolean, true if this importer can handle this file.
        """
        with open(file.name, 'r') as f:
            reader = csv.DictReader(f)
            # if data is not empty, return true
            for _ in reader:
                return True

        return False

    def extract(self, file, existing_entries=None):
        """Extract transactions from a file.

        If the importer would like to flag a returned transaction as a known
        duplicate, it may opt to set the special flag "__duplicate__" to True,
        and the transaction should be treated as a duplicate by the extraction
        code. This is a way to let the importer use particular information about
        previously imported transactions in order to flag them as duplicates.
        For example, if an importer has a way to get a persistent unique id for
        each of the imported transactions. (See this discussion for context:
        https://groups.google.com/d/msg/beancount/0iV-ipBJb8g/-uk4wsH2AgAJ)

        Args:
          file: A cache.FileMemo instance.
          existing_entries: An optional list of existing directives loaded from
            the ledger which is intended to contain the extracted entries. This
            is only provided if the user provides them via a flag in the
            extractor program.
        Returns:
          A list of new, imported directives (usually mostly Transactions)
          extracted from the file.
        """
        with open(file.name, 'r') as f:
            reader = csv.DictReader(f)
            entries = []

            for (index, entity) in enumerate(reader):
                description = Description(entity["类别"])
                meta = data.new_metadata(file.name, index)
                _datetime = datetime.strptime(
                    entity["日期"], "%Y-%m-%d %H:%M:%S")

                meta["time"] = str(_datetime.time())

                system, merchant = entity["机号"], entity["地点"]
                if description == Description.CONSUMPTION:
                    meta["system"] = system
                    meta["merchant"] = merchant

                amount = Amount(
                    Decimal(entity["金额"]).quantize(Decimal("1.00")), "CNY")

                postings = [
                    data.Posting(
                        self.account,
                        -amount,
                        None,
                        None,
                        None,
                        None,
                    ),
                ]

                account = Assets.FIXME.value
                if description == Description.CONSUMPTION:
                    account = self.category
                if description == Description.CHARGE:
                    account = self.bank

                postings.append(
                    data.Posting(
                        account,
                        amount,
                        None,
                        None,
                        None,
                        None,
                    ))

                txn = data.Transaction(meta, _datetime.date(), self.FLAG,
                                       PAYEE, description.value,
                                       data.EMPTY_SET, data.EMPTY_SET,
                                       postings)
                entries.append(txn)

            return entries


CONFIG = [
    USTCCardImporter(account="Assets:CN:Card:USTC",
                     bank=BANK_CARD,
                     category="Expenses:USTC:Cafeteria"),
]
