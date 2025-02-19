import logging
import os

import requests

from . import schemas
from .util import log

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.headers = {
            "Authorization": os.environ.get("AUTH"),
            "X-Akahu-ID": os.environ.get("AKAHU_ID"),
        }
        self.transaction_account_type = "CHECKING"

    @log
    def test(self) -> schemas.Test:
        return {"test": "Dw it's working king"}

    def get_accounts(self) -> list[schemas.Account]:
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
            if account["type"] == self.transaction_account_type
        ]

    def get_transactions(self) -> list[dict]:
        accounts = self.get_accounts()
        all_transactions = []
        for account in accounts:
            account_transactions = requests.get(
                f"https://api.akahu.io/v1/accounts/{account['_id']}/transactions",
                headers=self.headers,
            ).json()["items"]
            all_transactions += account_transactions
        return all_transactions
