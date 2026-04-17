import os
import json
import requests
import hashlib  # 用于生成哈希值对比文件是否变动


def get_md5(content):
    """计算内容的 MD5 值，用于判断内容是否发生改变"""
    if isinstance(content, (dict, list)):
        # 字典排序后再转 JSON，确保内容相同但顺序不同时 MD5 一致
        content = json.dumps(content, sort_keys=True)
    return hashlib.md5(str(content).encode('utf-8')).hexdigest()


def sync_webase_contracts():
    webase_url = os.environ.get("WEBASE_URL", "http://127.0.0.1:5002/WeBASE-Front").rstrip("/")
    url = f"{webase_url}/contract/contractList/multiPath"
    # 使用脚本相对路径，避免本机绝对路径泄露
    save_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "app", "sysadmin", "contrac"))

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    payload = {
        "groupId": 1,
        "contractPathList": ["power"]
    }

    has_changed = False  # 记录本次启动是否有任何文件发生变动

    try:
        print("正在检查 WeBASE 合约状态...")
        response = requests.post(url, json=payload, timeout=10)
        res_data = response.json()

        # 兼容 WeBASE 不同的返回结构
        contract_list = res_data if isinstance(res_data, list) else res_data.get('data', [])

        for contract in contract_list:
            if not isinstance(contract, dict):
                continue

            name = contract.get('contractName')
            if not name:
                continue

            # 提取数据
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

                # --- 核心修改：检查一致性 ---
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

                    print(f"检测到变更，正在更新: {name}{suffix}")
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content_str)
                    has_changed = True

        if has_changed:
            print(f"\n同步成功！部分文件已更新至: {save_dir}")
        else:
            print(f"\n检查完毕：本地文件与 WeBASE 保持一致，无需重新加载。")

        return has_changed

    except Exception as e:
        print(f"同步过程中出错: {e}")
        return False


if __name__ == "__main__":
    sync_webase_contracts()
