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


class PowerDeviceTestClient:
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

    def create_device(self, device_id, location, status, battery, capacity, function_type, username="", order_no=""):
        params = [
            int(device_id),
            str(location),
            str(status),
            int(battery),
            int(capacity),
            str(function_type),
            str(username),
            str(order_no),
        ]
        res = self.client.sendRawTransaction(self.address, self.abi, "createDevice", params)
        return self._receipt(res)

    def update_device(self, device_id, location, status, battery, capacity, function_type, username="", order_no=""):
        params = [
            int(device_id),
            str(location),
            str(status),
            int(battery),
            int(capacity),
            str(function_type),
            str(username),
            str(order_no),
        ]
        res = self.client.sendRawTransaction(self.address, self.abi, "updateDevice", params)
        return self._receipt(res)

    def delete_device(self, device_id):
        res = self.client.sendRawTransaction(self.address, self.abi, "deleteDevice", [int(device_id)])
        return self._receipt(res)

    def get_device(self, device_id):
        return self.client.call(self.address, self.abi, "getDevice", [int(device_id)])


if __name__ == "__main__":
    api = PowerDeviceTestClient()
    print("Device:", api.get_device(1))
