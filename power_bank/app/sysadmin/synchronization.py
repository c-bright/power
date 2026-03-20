# -*- coding: utf-8 -*-
import os
import json
import requests
import hashlib
import config  # 瀵煎叆浣犵殑涓ぎ閰嶇疆


# ----------------- 1. 鐜鑷剤涓庡垵濮嬪寲 -----------------
def ensure_env():
    """鍒濆鍖?SDK 鐜骞惰繑鍥炲叧閿矾寰?""
    sdk_path = getattr(config, 'SDK_PATH', r"E:\power_bank\FISCO-BCOS\python-sdk")
    log_dir = os.path.join(sdk_path, "bin", "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 鍒囨崲宸ヤ綔鐩綍浠ュ姞杞借瘉涔?
    os.chdir(sdk_path)

    this_dir = os.path.dirname(os.path.abspath(__file__))
    contrac_dir = os.path.join(this_dir, "contrac")
    conf_path = os.path.join(this_dir, "conf.py")

    return contrac_dir, conf_path


CONTRAC_DIR, CONF_PATH = ensure_env()

from client.bcosclient import BcosClient


# ----------------- 2. 宸ュ叿鍑芥暟 -----------------
def get_md5(content):
    """璁＄畻鍐呭鐨?MD5 鍊?""
    if isinstance(content, (dict, list)):
        content = json.dumps(content, sort_keys=True)
    return hashlib.md5(str(content).encode('utf-8')).hexdigest()


def update_local_conf(address_map):
    """銆愰摼涓?-> 閾句笅銆戝皢鍦板潃鍚屾鍥炴湰鍦?conf.py"""
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
    print(f"鏈湴閰嶇疆宸插悓姝ュ湴鍧€: {list(address_map.keys())}")


# ----------------- 3. WeBASE 浜や簰閫昏緫 -----------------
WEBASE_URL = os.environ.get("WEBASE_URL", "http://127.0.0.1:5002/WeBASE-Front")


def sync_from_webase():
    """浠?WeBASE 鑾峰彇鍚堢害鏁版嵁"""
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
        print(f" WeBASE 鍚屾澶辫触: {e}")
        return [], {}


def register_to_webase(name, address):
    """銆愰摼涓?-> 閾句笂銆戝憡鐭?WeBASE 鑴氭湰閮ㄧ讲鐨勬柊鍦板潃"""
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
        print(f"WeBASE 缃戦〉绔凡鍚屾鍦板潃: {name}")
    except:
        pass


# ----------------- 4. 涓绘祦姘寸嚎 -----------------
def run_dual_sync():
    print("鍚姩鍙屽悜鍚屾绯荤粺...")

    # 绗竴姝ワ細鑾峰彇杩滅▼鐘舵€?
    changed_names, remote_addrs = sync_from_webase()

    # 鍦烘櫙 A锛氶摼涓婇儴缃?-> 閾句笅鍚屾
    # 鍗充娇浠ｇ爜娌″彉锛屽鏋滆繙绋嬪湴鍧€鏇存柊浜嗭紝涔熻鍚屾缁欐湰鍦?
    if remote_addrs:
        update_local_conf(remote_addrs)

    # 鍦烘櫙 B锛氶摼涓嬮儴缃?-> 閾句笂鍚屾
    # 濡傛灉浠ｇ爜鍙戠敓浜嗗彉鍔紝鎵ц鏈湴閮ㄧ讲骞跺洖浼犲湴鍧€
    if not changed_names:
        print("鐘舵€佷竴鑷达紝鏃犻渶閲嶆柊閮ㄧ讲銆?)
        return

    print(f"妫€娴嬪埌浠ｇ爜鍙樻洿: {changed_names}锛屽紑濮嬭嚜鍔ㄩ儴缃?..")
    client = BcosClient()
    new_deployments = {}

    for name in changed_names:
        bin_path = os.path.join(CONTRAC_DIR, f"{name}.bin")
        try:
            with open(bin_path, 'r') as f:
                contract_bin = f.read().strip()

            print(f"閮ㄧ讲鍚堢害 [{name}] ...")
            result = client.deploy(contract_bin)
            addr = result['contractAddress']
            new_deployments[name] = addr

            # 鍚屾缁?WeBASE
            register_to_webase(name, addr)
        except Exception as e:
            print(f" {name} 閮ㄧ讲澶辫触: {e}")

    # 鏈€鍚庢洿鏂颁竴娆℃湰鍦伴厤缃?
    if new_deployments:
        update_local_conf(new_deployments)


if __name__ == "__main__":
    run_dual_sync()
