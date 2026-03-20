import os
import sys
import time
import json
import hashlib
import pymysql
import logging

from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, cast

from pymysql.cursors import DictCursor

from app.sysadmin import conf as config

if config.SDK_PATH not in sys.path:
    sys.path.insert(0, config.SDK_PATH)

os.chdir(config.SDK_PATH)
logging.disable(logging.ERROR)

from client.bcosclient import BcosClient  # noqa: E402
from eth_utils import to_checksum_address  # noqa: E402


class SuperSyncWorker:
    BIDIRECTIONAL_TABLES = ("admin", "users", "billing_rules", "Information")
    UPLOAD_ONLY_TABLES = ("feedback", "rent_record")

    def __init__(self):
        try:
            self.client = BcosClient()
            self.db = pymysql.connect(**config.MYSQL_CONFIG, cursorclass=DictCursor)
            self.abis: Dict[str, List[Dict[str, Any]]] = {}
            for name in ["AdminManager", "UserStorage", "PowerManager", "RentRecordManager", "FeedbackManager"]:
                self.abis[name] = self._load_abi(config.CONTRACT_CONFIG[name]["abi"])
        except Exception:
            sys.exit(1)

    @staticmethod
    def _load_abi(abi_path: str) -> List[Dict[str, Any]]:
        with open(abi_path, "r", encoding="utf-8") as f:
            abi = json.load(f)
        if isinstance(abi, str):
            abi = json.loads(abi)
        return cast(List[Dict[str, Any]], abi)

    @staticmethod
    def _is_success(res):
        if isinstance(res, dict):
            return res.get("status") == "0x0"
        return isinstance(res, str) and res.startswith("0x")

    @staticmethod
    def _get_hash(res):
        return res.get("transactionHash") if isinstance(res, dict) else str(res)

    @staticmethod
    def _generate_sync_hash(table, row_id):
        raw = f"{table}:{row_id}:{time.time_ns()}"
        return "sync_" + hashlib.sha1(raw.encode("utf-8")).hexdigest()

    def _mark(self, table, row_id, tx_hash=None):
        final_hash = tx_hash or self._generate_sync_hash(table, row_id)
        with self.db.cursor() as cursor:
            sql = f"UPDATE {table} SET sync_status = 1, tx_hash = %s, created_at = NOW() WHERE id = %s"
            cursor.execute(sql, (final_hash, row_id))
        self.db.commit()

    @staticmethod
    def _parse_db_time(value: Any) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
        return None

    @staticmethod
    def _parse_chain_time(value: Any) -> Optional[datetime]:
        if value in (None, "", 0, "0"):
            return None
        try:
            ts = int(value)
            if ts > 10 ** 12:
                ts = ts / 1000
            return datetime.fromtimestamp(ts)
        except Exception:
            return None

    @staticmethod
    def _db_is_newer(db_time, chain_time):
        if db_time and chain_time:
            return db_time >= chain_time
        return db_time is not None and chain_time is None

    def _safe_call(self, contract_name: str, func_name: str, params: List[Any]) -> Optional[Any]:
        try:
            return self.client.call(
                config.CONTRACT_CONFIG[contract_name]["address"],
                self.abis[contract_name],
                func_name,
                params,
            )
        except Exception:
            return None

    def _safe_send(self, contract_name: str, func_name: str, params: List[Any]) -> Optional[Any]:
        try:
            return self.client.sendRawTransaction(
                config.CONTRACT_CONFIG[contract_name]["address"],
                self.abis[contract_name],
                func_name,
                params,
            )
        except Exception:
            return None

    @staticmethod
    def _as_row_dict(row: Any) -> Dict[str, Any]:
        if isinstance(row, dict):
            return cast(Dict[str, Any], row)
        return {}

    @staticmethod
    def _as_sequence(data: Any) -> Sequence[Any]:
        if isinstance(data, (list, tuple)):
            return cast(Sequence[Any], data)
        return ()

    def _sync_admin_from_db(self):
        with self.db.cursor() as cursor:
            cursor.execute("SELECT * FROM admin")
            rows = cast(List[Dict[str, Any]], cursor.fetchall())

        for row in rows:
            try:
                row = self._as_row_dict(row)
                addr = to_checksum_address(row["address"])
                db_time = self._parse_db_time(row.get("created_at"))
                chain_data = self._safe_call("AdminManager", "getAdminByAddr", [addr])
                chain_seq = self._as_sequence(chain_data)

                if len(chain_seq) < 6:
                    params = [
                        addr,
                        row["username"],
                        int(row["can_manage_info"]),
                        int(row["can_manage_rules"]),
                        int(row["can_manage_feedback"]),
                        row.get("password") or "123456",
                    ]
                    res = self._safe_send("AdminManager", "createAdmin", params)
                    if self._is_success(res):
                        self._mark("admin", row["id"], self._get_hash(res))
                    continue

                chain_time = self._parse_chain_time(chain_seq[5])
                if self._db_is_newer(db_time, chain_time):
                    params = [
                        addr,
                        int(row["can_manage_info"]),
                        int(row["can_manage_rules"]),
                        int(row["can_manage_feedback"]),
                    ]
                    res = self._safe_send("AdminManager", "updateAdminPermission", params)
                    if self._is_success(res):
                        self._mark("admin", row["id"], self._get_hash(res))
                else:
                    with self.db.cursor() as cursor:
                        cursor.execute(
                            """
                            UPDATE admin
                            SET username = %s,
                                can_manage_info = %s,
                                can_manage_rules = %s,
                                can_manage_feedback = %s,
                                created_at = %s,
                                sync_status = 1,
                                tx_hash = %s
                            WHERE id = %s
                            """,
                            (
                                chain_seq[0],
                                int(chain_seq[1]),
                                int(chain_seq[2]),
                                int(chain_seq[3]),
                                chain_time,
                                self._generate_sync_hash("admin", row["id"]),
                                row["id"],
                            ),
                        )
                    self.db.commit()
            except Exception:
                continue

    def _sync_admin_from_chain(self):
        count_res = self._safe_call("AdminManager", "getAdminCount", [])
        count_seq = self._as_sequence(count_res)
        if not count_seq:
            return

        try:
            first = count_seq[0]
            count = int(first[0] if isinstance(first, (list, tuple)) else first)
        except Exception:
            return

        with self.db.cursor() as cursor:
            for i in range(count):
                try:
                    chain_addr = self._safe_call("AdminManager", "adminList", [i])
                    if not chain_addr:
                        continue
                    if isinstance(chain_addr, (list, tuple)):
                        chain_addr = chain_addr[0]
                    actual_data = self._safe_call("AdminManager", "getAdminByAddr", [chain_addr])
                    actual_seq = self._as_sequence(actual_data)
                    if len(actual_seq) < 6:
                        continue

                    chain_time = self._parse_chain_time(actual_seq[5])
                    cursor.execute("SELECT id, created_at FROM admin WHERE address = %s", (chain_addr,))
                    local_row = self._as_row_dict(cursor.fetchone())

                    if not local_row:
                        cursor.execute(
                            """
                            INSERT INTO admin (
                                username, address, password, can_manage_info,
                                can_manage_rules, can_manage_feedback, created_at, sync_status, tx_hash
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, 1, %s)
                            """,
                            (
                                actual_seq[0],
                                chain_addr,
                                actual_seq[4] or "123456",
                                int(actual_seq[1]),
                                int(actual_seq[2]),
                                int(actual_seq[3]),
                                chain_time,
                                self._generate_sync_hash("admin", chain_addr),
                            ),
                        )
                        continue

                    db_time = self._parse_db_time(local_row.get("created_at"))
                    if chain_time and (not db_time or chain_time > db_time):
                        cursor.execute(
                            """
                            UPDATE admin
                            SET username = %s,
                                password = %s,
                                can_manage_info = %s,
                                can_manage_rules = %s,
                                can_manage_feedback = %s,
                                created_at = %s,
                                sync_status = 1,
                                tx_hash = %s
                            WHERE id = %s
                            """,
                            (
                                actual_seq[0],
                                actual_seq[4] or "123456",
                                int(actual_seq[1]),
                                int(actual_seq[2]),
                                int(actual_seq[3]),
                                chain_time,
                                self._generate_sync_hash("admin", local_row["id"]),
                                local_row["id"],
                            ),
                        )
                except Exception:
                    continue
        self.db.commit()

    def _sync_users_bidirectional(self):
        with self.db.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            rows = cast(List[Dict[str, Any]], cursor.fetchall())

        for row in rows:
            try:
                row = self._as_row_dict(row)
                addr = to_checksum_address(row["address"])
                db_time = self._parse_db_time(row.get("created_at"))
                chain_data = self._safe_call("UserStorage", "getUser", [addr])
                chain_seq = self._as_sequence(chain_data)

                if len(chain_seq) < 6:
                    params = [
                        addr,
                        row["username"],
                        row["password"],
                        row["email"],
                        int(float(row["balance"]) * 10 ** 8),
                        row.get("remark") or "",
                    ]
                    res = self._safe_send("UserStorage", "createUser", params)
                    if self._is_success(res):
                        self._mark("users", row["id"], self._get_hash(res))
                    continue

                chain_time = self._parse_chain_time(chain_seq[5])
                if self._db_is_newer(db_time, chain_time):
                    params = [
                        addr,
                        row["password"],
                        row["email"],
                        int(float(row["balance"]) * 10 ** 8),
                        row.get("remark") or "",
                    ]
                    res = self._safe_send("UserStorage", "updateUser", params)
                    if self._is_success(res):
                        self._mark("users", row["id"], self._get_hash(res))
                else:
                    with self.db.cursor() as cursor:
                        cursor.execute(
                            """
                            UPDATE users
                            SET username = %s,
                                password = %s,
                                email = %s,
                                balance = %s,
                                remark = %s,
                                created_at = %s,
                                sync_status = 1,
                                tx_hash = %s
                            WHERE id = %s
                            """,
                            (
                                chain_seq[0],
                                chain_seq[1],
                                chain_seq[2],
                                float(chain_seq[3]) / 10 ** 8,
                                chain_seq[4],
                                chain_time,
                                self._generate_sync_hash("users", row["id"]),
                                row["id"],
                            ),
                        )
                    self.db.commit()
            except Exception:
                continue

    def _sync_billing_rules_bidirectional(self):
        with self.db.cursor() as cursor:
            cursor.execute("SELECT * FROM billing_rules ORDER BY id DESC LIMIT 1")
            row = self._as_row_dict(cursor.fetchone())

        if not row:
            return

        chain_data = self._safe_call("PowerManager", "currentRule", [])
        chain_seq = self._as_sequence(chain_data)
        db_time = self._parse_db_time(row.get("created_at"))

        if len(chain_seq) < 5:
            params = [
                int(row["free_minutes"]),
                int(float(row["hourly_price"])),
                int(float(row["daily_max"])),
                int(float(row["deposit"])),
            ]
            res = self._safe_send("PowerManager", "updateBillingRule", params)
            if self._is_success(res):
                self._mark("billing_rules", row["id"], self._get_hash(res))
            return

        chain_time = self._parse_chain_time(chain_seq[4])
        if self._db_is_newer(db_time, chain_time):
            params = [
                int(row["free_minutes"]),
                int(float(row["hourly_price"])),
                int(float(row["daily_max"])),
                int(float(row["deposit"])),
            ]
            res = self._safe_send("PowerManager", "updateBillingRule", params)
            if self._is_success(res):
                self._mark("billing_rules", row["id"], self._get_hash(res))
        else:
            with self.db.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE billing_rules
                    SET free_minutes = %s,
                        hourly_price = %s,
                        daily_max = %s,
                        deposit = %s,
                        created_at = %s,
                        sync_status = 1,
                        tx_hash = %s
                    WHERE id = %s
                    """,
                    (
                        int(chain_seq[0]),
                        float(chain_seq[1]),
                        float(chain_seq[2]),
                        float(chain_seq[3]),
                        chain_time,
                        self._generate_sync_hash("billing_rules", row["id"]),
                        row["id"],
                    ),
                )
            self.db.commit()

    def _sync_information_bidirectional(self):
        with self.db.cursor() as cursor:
            cursor.execute("SELECT * FROM Information")
            rows = cast(List[Dict[str, Any]], cursor.fetchall())

        for row in rows:
            try:
                row = self._as_row_dict(row)
                chain_data = self._safe_call("PowerManager", "getDevice", [int(row["id"])])
                chain_seq = self._as_sequence(chain_data)
                db_time = self._parse_db_time(row.get("created_at"))
                params = [
                    int(row["id"]),
                    row["location"],
                    row["status"],
                    int(row["battery_level"]),
                    self._capacity_to_int(row["capacity"]),
                    row["function_type"],
                    row.get("username") or "",
                    row.get("order_no") or "",
                ]

                if len(chain_seq) < 8:
                    res = self._safe_send("PowerManager", "createDevice", params)
                    if self._is_success(res):
                        self._mark("Information", row["id"], self._get_hash(res))
                    continue

                chain_time = self._parse_chain_time(chain_seq[7])
                if self._db_is_newer(db_time, chain_time):
                    res = self._safe_send("PowerManager", "updateDevice", params)
                    if self._is_success(res):
                        self._mark("Information", row["id"], self._get_hash(res))
                else:
                    with self.db.cursor() as cursor:
                        cursor.execute(
                            """
                            UPDATE Information
                            SET location = %s,
                                status = %s,
                                battery_level = %s,
                                capacity = %s,
                                function_type = %s,
                                username = %s,
                                order_no = %s,
                                created_at = %s,
                                sync_status = 1,
                                tx_hash = %s
                            WHERE id = %s
                            """,
                            (
                                chain_seq[0],
                                chain_seq[1],
                                int(chain_seq[2]),
                                self._capacity_from_chain(chain_seq[3]),
                                chain_seq[4],
                                chain_seq[5] or None,
                                chain_seq[6] or None,
                                chain_time,
                                self._generate_sync_hash("Information", row["id"]),
                                row["id"],
                            ),
                        )
                    self.db.commit()
            except Exception:
                continue

    def _upload_feedback_to_chain(self):
        with self.db.cursor() as cursor:
            cursor.execute("SELECT * FROM feedback WHERE sync_status = 0")
            rows = cast(List[Dict[str, Any]], cursor.fetchall())

        for row in rows:
            try:
                row = self._as_row_dict(row)
                reply = row.get("Reply") or row.get("reply") or ""
                params = [
                    str(row["order_no"]),
                    str(row["username"]),
                    str(row.get("content") or ""),
                    str(row.get("status") or "pending"),
                    str(reply),
                ]
                res = self._safe_send("FeedbackManager", "createDispute", params)
                if self._is_success(res):
                    self._mark("feedback", row["id"], self._get_hash(res))
            except Exception:
                continue

    def _upload_rent_record_to_chain(self):
        with self.db.cursor() as cursor:
            cursor.execute("SELECT * FROM rent_record WHERE sync_status = 0")
            rows = cast(List[Dict[str, Any]], cursor.fetchall())

        for row in rows:
            try:
                row = self._as_row_dict(row)
                params = [
                    row["order_no"],
                    row["location"],
                    row.get("username") or "guest",
                    int(float(row["cost"]) * 100),
                    row["status"],
                    str(row["rent_time"]),
                    str(row.get("return_time") or ""),
                    self._capacity_to_int(row["capacity"]),
                    row["function_type"],
                ]
                res = self._safe_send("RentRecordManager", "syncRecord", params)
                if self._is_success(res):
                    self._mark("rent_record", row["id"], self._get_hash(res))
            except Exception:
                continue

    @staticmethod
    def _capacity_to_int(value: Any) -> int:
        mapping = {"small": 1, "medium": 2, "large": 3}
        return mapping.get(str(value).lower(), 2)

    @staticmethod
    def _capacity_from_chain(value: Any) -> str:
        mapping = {1: "small", 2: "medium", 3: "large"}
        try:
            return mapping.get(int(value), "medium")
        except Exception:
            return "medium"

    def sync_bidirectional_tables(self):
        self._sync_admin_from_db()
        self._sync_admin_from_chain()
        self._sync_users_bidirectional()
        self._sync_billing_rules_bidirectional()
        self._sync_information_bidirectional()

    def sync_upload_only_tables(self):
        self._upload_feedback_to_chain()
        self._upload_rent_record_to_chain()

    def run(self):
        while True:
            try:
                self.sync_bidirectional_tables()
                self.sync_upload_only_tables()
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] sync ok")
                time.sleep(10)
            except KeyboardInterrupt:
                raise SystemExit(0)
            except Exception:
                time.sleep(5)


if __name__ == "__main__":
    SuperSyncWorker().run()
