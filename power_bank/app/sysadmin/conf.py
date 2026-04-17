# -*- coding: utf-8 -*-
"""区块链与合约配置。路径基于当前包目录，便于迁移。"""
import os

# 当前包目录（app/sysadmin/）
_this_dir = os.path.dirname(os.path.abspath(__file__))
_contrac_dir = os.path.join(_this_dir, "contrac")

# SDK 路径：优先环境变量，否则默认相对项目上级
SDK_PATH = os.environ.get("FISCO_SDK_PATH") or os.path.normpath(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_this_dir))), "FISCO-BCOS", "python-sdk")
)

MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "power")
}

# 合约 ABI 路径使用相对当前包
CONTRACT_CONFIG = {
    "AdminManager": {
        "address": "0x7d1c6e8e3d6b8090e76a1d3c2717fd532fdfdfad",
        "abi": os.path.join(_contrac_dir, "AdminManager.abi")
    },
    "FeedbackManager": {
        "address": "0x670bfc6fb11e889547ff47f8eb38d0e87dfdef30",
        "abi": os.path.join(_contrac_dir, "FeedbackManager.abi")
    },
    "PowerManager": {
        "address": "0x6b4045ecd74050508751b4108944fb6b2c4905c3",
        "abi": os.path.join(_contrac_dir, "PowerManager.abi")
    },
    "RentRecordManager": {
        "address": "0x0c3b9368f59e0b9363c2d91edb9d4143f23a3a99",
        "abi": os.path.join(_contrac_dir, "RentRecordManager.abi")
    },
    "UserStorage": {
        "address": "0xc4e0e89109b8c10a23ffb2d51fc3861b5ec566e7",
        "abi": os.path.join(_contrac_dir, "UserStorage.abi")
    }
}



