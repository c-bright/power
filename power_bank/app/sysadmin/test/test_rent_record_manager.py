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
from client.bcoserror import BcosException


class RentRecordManagerTestClient:
    def __init__(self):
        self.client = BcosClient()
        self.address = config.CONTRACT_CONFIG["RentRecordManager"]["address"]
        self.abi = self._load_abi(config.CONTRACT_CONFIG["RentRecordManager"]["abi"])

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

    def sync_record(self, order_no, location, username, cost, status, rent_time, return_time, capacity, function_type):
        params = [
            str(order_no),
            str(location),
            str(username),
            int(cost),
            str(status),
            str(rent_time),
            str(return_time),
            int(capacity),
            str(function_type),
        ]
        res = self.client.sendRawTransaction(self.address, self.abi, "syncRecord", params)
        return self._receipt(res)

    def get_record(self, order_no):
        safe_order_no = str(order_no)
        try:
            return self.client.call(self.address, self.abi, "getRecord", [safe_order_no])
        except BcosException as exc:
            if "Revert instruction" in str(exc):
                return {
                    "ok": False,
                    "order_no": safe_order_no,
                    "message": "链上不存在该订单，或合约在 getRecord 中对该订单执行了 revert。",
                }
            raise

if __name__ == "__main__":
    api = RentRecordManagerTestClient()
    print("Record:", api.get_record("ORD202512240066"))
