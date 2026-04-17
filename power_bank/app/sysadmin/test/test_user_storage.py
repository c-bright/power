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
from eth_utils import to_checksum_address


class UserStorageTestClient:
    def __init__(self):
        self.client = BcosClient()
        self.address = config.CONTRACT_CONFIG["UserStorage"]["address"]
        self.abi = self._load_abi(config.CONTRACT_CONFIG["UserStorage"]["abi"])

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

    def create_user(self, addr, username, password, email, balance=0.00, remark=""):
        params = [to_checksum_address(addr), username, password, email, int(balance), remark]
        res = self.client.sendRawTransaction(self.address, self.abi, "createUser", params)
        return self._receipt(res)

    def update_user(self, addr, password, email, balance, remark=""):
        params = [to_checksum_address(addr), password, email, int(balance), remark]
        res = self.client.sendRawTransaction(self.address, self.abi, "updateUser", params)
        return self._receipt(res)

    def delete_user(self, addr):
        res = self.client.sendRawTransaction(self.address, self.abi, "deleteUser", [to_checksum_address(addr)])
        return self._receipt(res)

    def get_user(self, addr):
        safe_addr = to_checksum_address(addr)
        try:
            return self.client.call(self.address, self.abi, "getUser", [safe_addr])
        except BcosException as exc:
            if "Revert instruction" in str(exc):
                return {
                    "ok": False,
                    "address": safe_addr,
                    "message": "链上不存在该用户，或合约在 getUser 中对该地址执行了 revert。",
                }
            raise


if __name__ == "__main__":
    api = UserStorageTestClient()
    print("User:", api.get_user("0x6ecac2ea779fac087314f2ec7659dfb07a38740c"))
