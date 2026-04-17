# -*- coding: utf-8 -*-
import os
import json
import requests
import hashlib
from app import config



def ensure_env():
    """初始化 SDK 环境并返回关键路径"""
    sdk_path = os.environ.get("FISCO_SDK_PATH") or getattr(config, 'SDK_PATH', os.path.normpath(os.path.join(os.getcwd(), "FISCO-BCOS", "python-sdk")))
    log_dir = os.path.join(sdk_path, "bin", "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 切换工作目录以加载证书
    os.chdir(sdk_path)

    this_dir = os.path.dirname(os.path.abspath(__file__))
    contrac_dir = os.path.join(this_dir, "contrac")
    conf_path = os.path.join(this_dir, "conf.py")

    return contrac_dir, conf_path


CONTRAC_DIR, CONF_PATH = ensure_env()

from client.bcosclient import BcosClient


# ----------------- 2. 工具函数 -----------------
def get_md5(content):
    """计算内容的 MD5 值"""
    if isinstance(content, (dict, list)):
        content = json.dumps(content, sort_keys=True)
    return hashlib.md5(str(content).encode('utf-8')).hexdigest()


def update_local_conf(address_map):
    """【链上 -> 链下】将地址同步回本地 conf.py"""
    if not address_map:
        return
    with open(CONF_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    current_contract = None
    for line in lines:
        for name in address_map.keys():
            if f'"{name}"' in line:
                current_contract = name
                break
        if current_contract and '"address":' in line:
            indent = line[:line.find('"address"')]
            new_lines.append(f'{indent}"address": "{address_map[current_contract]}",\n')
            current_contract = None
        else:
            new_lines.append(line)

    with open(CONF_PATH, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"本地配置已同步地址: {list(address_map.keys())}")


# ----------------- 3. WeBASE 交互逻辑 -----------------
WEBASE_URL = os.environ.get("WEBASE_URL", "http://127.0.0.1:5002/WeBASE-Front")


def sync_from_webase():
    """从 WeBASE 获取合约数据"""
    url = f"{WEBASE_URL}/contract/contractList/multiPath"
    payload = {"groupId": 1, "contractPathList": ["power"]}

    changed_contracts = []
    remote_addresses = {}

    try:
        res = requests.post(url, json=payload, timeout=5).json()
        contracts = res if isinstance(res, list) else res.get('data', [])

        for c in contracts:
            name = c['contractName']
            new_bin = c.get('bytecodeBin') or c.get('contractBin')
            if not new_bin: continue


            bin_path = os.path.join(CONTRAC_DIR, f"{name}.bin")
            is_new = True
            if os.path.exists(bin_path):
                with open(bin_path, 'r') as f:
                    if get_md5(f.read()) == get_md5(new_bin):
                        is_new = False

            if is_new:

                with open(bin_path, 'w') as f: f.write(new_bin)
                with open(os.path.join(CONTRAC_DIR, f"{name}.abi"), 'w') as f:
                    f.write(json.dumps(c['contractAbi']))
                changed_contracts.append(name)


            if c.get('contractAddress'):
                remote_addresses[name] = c['contractAddress']

        return changed_contracts, remote_addresses
    except Exception as e:
        print(f" WeBASE 同步失败: {e}")
        return [], {}


def register_to_webase(name, address):
    """【链下 -> 链上】告知 WeBASE 脚本部署的新地址"""
    url = f"{WEBASE_URL}/contract/save"
    abi_path = os.path.join(CONTRAC_DIR, f"{name}.abi")
    with open(abi_path, 'r') as f:
        abi = json.load(f)

    payload = {
        "groupId": 1,
        "contractName": name,
        "contractPath": "power",
        "contractAddress": address,
        "contractAbi": json.dumps(abi)
    }
    try:
        requests.post(url, json=payload, timeout=5)
        print(f"WeBASE 网页端已同步地址: {name}")
    except:
        pass


# ----------------- 4. 主流水线 -----------------
def run_dual_sync():
    print("启动双向同步系统...")

    # 第一步：获取远程状态
    changed_names, remote_addrs = sync_from_webase()

    # 场景 A：链上部署 -> 链下同步
    # 即使代码没变，如果远程地址更新了，也要同步给本地
    if remote_addrs:
        update_local_conf(remote_addrs)

    # 场景 B：链下部署 -> 链上同步
    # 如果代码发生了变动，执行本地部署并回传地址
    if not changed_names:
        print("状态一致，无需重新部署。")
        return

    print(f"检测到代码变更: {changed_names}，开始自动部署...")
    client = BcosClient()
    new_deployments = {}

    for name in changed_names:
        bin_path = os.path.join(CONTRAC_DIR, f"{name}.bin")
        try:
            with open(bin_path, 'r') as f:
                contract_bin = f.read().strip()

            print(f"部署合约 [{name}] ...")
            result = client.deploy(contract_bin)
            addr = result['contractAddress']
            new_deployments[name] = addr

            # 同步给 WeBASE
            register_to_webase(name, addr)
        except Exception as e:
            print(f" {name} 部署失败: {e}")

    # 最后更新一次本地配置
    if new_deployments:
        update_local_conf(new_deployments)


if __name__ == "__main__":
    run_dual_sync()
