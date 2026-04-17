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


class FeedbackManagerTestClient:
    def __init__(self):
        self.client = BcosClient()
        self.address = config.CONTRACT_CONFIG["FeedbackManager"]["address"]
        self.abi = self._load_abi(config.CONTRACT_CONFIG["FeedbackManager"]["abi"])

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

    def create_dispute(self, order_no, username, content, status, reply=""):
        params = [str(order_no), str(username), str(content), str(status), str(reply)]
        res = self.client.sendRawTransaction(self.address, self.abi, "createDispute", params)
        return self._receipt(res)

    def get_dispute(self, order_no):
        return self.client.call(self.address, self.abi, "getDispute", [str(order_no)])


if __name__ == "__main__":
    api = FeedbackManagerTestClient()
    print("Dispute:", api.get_dispute("ORD20251220022954"))
