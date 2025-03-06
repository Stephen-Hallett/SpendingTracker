import logging
import os
from datetime import datetime, timedelta
import pytz

import polars as pl
import requests

from .schemas import Account, SpendingSummary, Test, Transaction
from .util import log

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.headers = {
            "Authorization": os.environ.get("AUTH"),
            "X-Akahu-ID": os.environ.get("AKAHU_ID"),
        }
        self.transaction_account_types = ["CHECKING", "CREDITCARD"]
        self.tz = pytz.timezone('Pacific/Auckland')

    @log
    def test(self) -> Test:
        return {"test": "Dw it's working king"}

    def get_accounts(self) -> list[Account]:
        akahu_accounts = requests.get(
            "https://api.akahu.io/v1/accounts", headers=self.headers
        ).json()["items"]
        return [
            {
                "_id": account["_id"],
                "name": account["name"],
                "company": account["connection"]["name"],
                "amount": account["balance"]["available"],
            }
            for account in akahu_accounts
            if account["type"] in self.transaction_account_types
        ]

    def get_transactions(self) -> list[Transaction]:
        accounts = self.get_accounts()
        all_transactions = []
        for account in accounts:
            account_transactions = requests.get(
                f"https://api.akahu.io/v1/accounts/{account['_id']}/transactions",
                headers=self.headers,
            ).json()["items"]
            for transaction in account_transactions:
                # Dates are stored in UTC, converting to NZDT is easiest
                transaction["date"] = datetime.strptime(transaction["date"], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=13, minutes=1)
                all_transactions.append(Transaction.model_validate(transaction))
        return all_transactions

    def spending_summary(self) -> SpendingSummary:
        all_transactions = pl.DataFrame(self.get_transactions())
        ctx = pl.SQLContext(df=all_transactions)
        dt = datetime.now(self.tz)
        week_start = dt - timedelta(
            days=dt.weekday(), hours=dt.hour, minutes=dt.minute, seconds=dt.second
        )
        week_start_str = week_start.strftime("%Y-%m-%d %H:%M:%S")

        month_start = dt - timedelta(
            days=dt.day-1, hours=dt.hour, minutes=dt.minute, seconds=dt.second
        )
        month_start_str = month_start.strftime("%Y-%m-%d %H:%M:%S")

        this_week = ctx.execute(
            f"SELECT * FROM df WHERE df.date > '{week_start_str}' AND type = 'DEBIT'"  # NOQA
        ).collect()
        this_month = ctx.execute(
            f"SELECT * FROM df WHERE df.date > '{month_start_str}' AND type = 'DEBIT'"  # NOQA
        ).collect()

        return {
            "Week": abs(this_week["amount"].sum()),
            "Month": abs(this_month["amount"].sum()),
        }
