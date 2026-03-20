# -*- coding: utf-8 -*-
"""区块链与合约配置。路径基于当前包目录，便于迁移。"""
import os

_this_dir = os.path.dirname(os.path.abspath(__file__))
_contrac_dir = os.path.join(_this_dir, "contrac")

SDK_PATH = os.environ.get("FISCO_SDK_PATH") or os.path.normpath(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_this_dir))), "FISCO-BCOS", "python-sdk")
)

MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "power")
}

CONTRACT_CONFIG = {
    "AdminManager": {
        "address": os.environ.get("ADMIN_MANAGER_ADDRESS", ""),
        "abi": os.path.join(_contrac_dir, "AdminManager.abi")
    },
    "FeedbackManager": {
        "address": os.environ.get("FEEDBACK_MANAGER_ADDRESS", ""),
        "abi": os.path.join(_contrac_dir, "FeedbackManager.abi")
    },
    "PowerManager": {
        "address": os.environ.get("POWER_MANAGER_ADDRESS", ""),
        "abi": os.path.join(_contrac_dir, "PowerManager.abi")
    },
    "RentRecordManager": {
        "address": os.environ.get("RENT_RECORD_MANAGER_ADDRESS", ""),
        "abi": os.path.join(_contrac_dir, "RentRecordManager.abi")
    },
    "UserStorage": {
        "address": os.environ.get("USER_STORAGE_ADDRESS", ""),
        "abi": os.path.join(_contrac_dir, "UserStorage.abi")
    }
}
