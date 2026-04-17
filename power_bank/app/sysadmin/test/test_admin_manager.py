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
from eth_utils import to_checksum_address


class AdminManagerTestClient:
    def __init__(self):
        self.client = BcosClient()
        self.address = config.CONTRACT_CONFIG["AdminManager"]["address"]
        self.abi = self._load_abi(config.CONTRACT_CONFIG["AdminManager"]["abi"])

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

    def create_admin(self, addr, username, can_manage_info, can_manage_rules, can_manage_feedback, password):
        params = [
            to_checksum_address(addr),
            username,
            int(can_manage_info),
            int(can_manage_rules),
            int(can_manage_feedback),
            password,
        ]
        res = self.client.sendRawTransaction(self.address, self.abi, "createAdmin", params)
        return self._receipt(res)

    def update_admin_permission(self, addr, can_manage_info, can_manage_rules, can_manage_feedback):
        params = [
            to_checksum_address(addr),
            int(can_manage_info),
            int(can_manage_rules),
            int(can_manage_feedback),
        ]
        res = self.client.sendRawTransaction(self.address, self.abi, "updateAdminPermission", params)
        return self._receipt(res)

    def delete_admin(self, addr):
        res = self.client.sendRawTransaction(
            self.address, self.abi, "deleteAdmin", [to_checksum_address(addr)]
        )
        return self._receipt(res)

    def get_admin_count(self):
        return self.client.call(self.address, self.abi, "getAdminCount", [])

    def get_admin_by_addr(self, addr):
        return self.client.call(self.address, self.abi, "getAdminByAddr", [to_checksum_address(addr)])

    def get_admin_address_by_index(self, index):
        return self.client.call(self.address, self.abi, "adminList", [int(index)])


if __name__ == "__main__":
    api = AdminManagerTestClient()
    print("Admin count:", api.get_admin_by_addr("0x534afdd38b6f12f3d9721705fc05752b79c612db"))
    print(type(api.get_admin_by_addr("0x534afdd38b6f12f3d9721705fc05752b79c612db")))
