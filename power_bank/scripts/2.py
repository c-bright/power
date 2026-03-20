import os
import json
import requests
import hashlib  # 鐢ㄤ簬鐢熸垚鍝堝笇鍊煎姣旀枃浠舵槸鍚﹀彉鍔?


def get_md5(content):
    """璁＄畻鍐呭鐨?MD5 鍊硷紝鐢ㄤ簬鍒ゆ柇鍐呭鏄惁鍙戠敓鏀瑰彉"""
    if isinstance(content, (dict, list)):
        # 瀛楀吀鎺掑簭鍚庡啀杞?JSON锛岀‘淇濆唴瀹圭浉鍚屼絾椤哄簭涓嶅悓鏃?MD5 涓€鑷?
        content = json.dumps(content, sort_keys=True)
    return hashlib.md5(str(content).encode('utf-8')).hexdigest()


def sync_webase_contracts():
    url = "http://127.0.0.1:5002/WeBASE-Front/contract/contractList/multiPath"
    # 浣跨敤缁濆璺緞纭繚鍑嗙‘
    save_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "app", "sysadmin", "contrac"))

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    payload = {
        "groupId": 1,
        "contractPathList": ["power"]
    }

    has_changed = False  # 璁板綍鏈鍚姩鏄惁鏈変换浣曟枃浠跺彂鐢熷彉鍔?

    try:
        print("姝ｅ湪妫€鏌?WeBASE 鍚堢害鐘舵€?..")
        response = requests.post(url, json=payload, timeout=10)
        res_data = response.json()

        # 鍏煎 WeBASE 涓嶅悓鐨勮繑鍥炵粨鏋?
        contract_list = res_data if isinstance(res_data, list) else res_data.get('data', [])

        for contract in contract_list:
            if not isinstance(contract, dict):
                continue

            name = contract.get('contractName')
            if not name:
                continue

            # 鎻愬彇鏁版嵁
            abi_content = contract.get('contractAbi')
            bin_content = contract.get('bytecodeBin') or contract.get('contractBin')
            src_content = contract.get('contractSource')

            files_map = {
                ".abi": abi_content,
                ".bin": bin_content,
                ".sol": src_content
            }

            for suffix, content in files_map.items():
                if not content:
                    continue

                file_path = os.path.join(save_dir, f"{name}{suffix}")

                # --- 鏍稿績淇敼锛氭鏌ヤ竴鑷存€?---
                new_content_str = json.dumps(content) if (suffix == ".abi" and not isinstance(content, str)) else str(
                    content)
                new_md5 = get_md5(new_content_str)

                is_identical = False
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        old_content = f.read()
                        if get_md5(old_content) == new_md5:
                            is_identical = True

                if not is_identical:

                    print(f"妫€娴嬪埌鍙樻洿锛屾鍦ㄦ洿鏂? {name}{suffix}")
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content_str)
                    has_changed = True

        if has_changed:
            print(f"\n鍚屾鎴愬姛锛侀儴鍒嗘枃浠跺凡鏇存柊鑷? {save_dir}")
        else:
            print(f"\n妫€鏌ュ畬姣曪細鏈湴鏂囦欢涓?WeBASE 淇濇寔涓€鑷达紝鏃犻渶閲嶆柊鍔犺浇銆?)

        return has_changed

    except Exception as e:
        print(f"鍚屾杩囩▼涓嚭閿? {e}")
        return False


if __name__ == "__main__":
    sync_webase_contracts()
