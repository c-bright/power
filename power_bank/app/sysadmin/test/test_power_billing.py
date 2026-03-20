import json
import logging
import os
import sys
import time

from app.sysadmin import conf as config

if config.SDK_PATH not in sys.path:
    sys.path.insert(0, config.SDK_PATH)

os.chdir(config.SDK_PATH)
logging.disable(logging.ERROR)

from client.bcosclient import BcosClient


class PowerBillingTestClient:
    def __init__(self):
        self.client = BcosClient()
        self.address = config.CONTRACT_CONFIG["PowerManager"]["address"]
        self.abi = self._load_abi(config.CONTRACT_CONFIG["PowerManager"]["abi"])

    @staticmethod
    def _load_abi(abi_path):
        with open(abi_path, "r", encoding="utf-8") as f:
            abi = json.load(f)
        if isinstance(abi, str):
            abi = json.loads(abi)
        return abi

    def _receipt(self, res):
        tx_hash = res if isinstance(res, str) else res.get("transactionHash")
        if not tx_hash:
            return None
        time.sleep(1)
        return self.client.getTransactionReceipt(tx_hash)

    def update_billing_rule(self, free_minutes, hourly_price, daily_max, deposit):
        params = [int(free_minutes), int(hourly_price), int(daily_max), int(deposit)]
        res = self.client.sendRawTransaction(self.address, self.abi, "updateBillingRule", params)
        return self._receipt(res)

    def get_billing_rule(self):
        return self.client.call(self.address, self.abi, "getBillingRule", [])

    def current_rule(self):
        return self.client.call(self.address, self.abi, "currentRule", [])


if __name__ == "__main__":
    api = PowerBillingTestClient()
    # api.update_billing_rule(5,3,30,99)
    print("Billing rule:", api.current_rule())
