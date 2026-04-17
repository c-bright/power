import sys
import os
sys.path.insert(0, os.getcwd())

print("=== 完整配置验证 ===")
print("")

try:
    from client_config import client_config
    print(" 1. 配置导入成功")
    
    # 检查所有必须的配置项
    print("\n 2. 配置项完整性检查:")
    
    config_categories = {
        "SDK算法类型配置": [
            ("crypto_type", "ECDSA"),
            ("ssl_type", "ECDSA")
        ],
        "通用配置": [
            ("contract_info_file", "bin/contract.ini"),
            ("account_keyfile_path", "bin/accounts"), 
            ("logdir", "bin/logs"),
            ("contract_dir", "./contracts")
        ],
        "账户配置": [
            ("account_keyfile", "pyaccount.keystore"),
            ("account_password", "123456"),
            ("gm_account_keyfile", "gm_account.json"),
            ("gm_account_password", "123456")
        ],
        "群组配置": [
            ("fiscoChainId", 1),
            ("groupid", 1)
        ],
        "通信配置": [
            ("client_protocol", "channel"),
            ("remote_rpcurl", "http://127.0.0.1:8545"),
            ("channel_host", "192.168.211.133"),
            ("channel_port", 20200)
        ],
        "证书配置": [
            ("channel_ca", "bin/ca.crt"),
            ("channel_node_cert", "bin/sdk.crt"),
            ("channel_node_key", "bin/sdk.key")
        ]
    }
    
    all_good = True
    for category, items in config_categories.items():
        print(f"\n{category}:")
        for name, expected in items:
            if hasattr(client_config, name):
                value = getattr(client_config, name)
                status = "" if str(value) == str(expected) else ""
                print(f"  {status} {name}: {value}")
                if str(value) != str(expected):
                    all_good = False
            else:
                print(f"   {name}: 缺失")
                all_good = False
    
    print("\n 3. 文件存在性检查:")
    
    # 检查账户文件
    account_file = client_config.account_keyfile
    account_exists = os.path.exists(account_file)
    if not account_exists and account_file == "pyaccount.keystore":
        # 检查是否在accounts目录下
        alt_path = os.path.join(client_config.account_keyfile_path, account_file)
        if os.path.exists(alt_path):
            account_exists = True
            print(f"   账户文件: {alt_path} (自动找到)")
        else:
            print(f"   账户文件: {account_file} (未找到)")
    else:
        print(f"  {'' if account_exists else ''} 账户文件: {account_file}")
    
    # 检查证书文件
    cert_exists = os.path.exists(client_config.channel_node_cert)
    key_exists = os.path.exists(client_config.channel_node_key)
    ca_exists = os.path.exists(client_config.channel_ca)
    
    print(f"  {'' if cert_exists else ''} SDK证书: {client_config.channel_node_cert}")
    print(f"  {'' if key_exists else ''} SDK私钥: {client_config.channel_node_key}")
    print(f"  {'' if ca_exists else ''} CA证书: {client_config.channel_ca}")
    
    print(f"\n{' 所有配置验证通过！' if all_good and account_exists and cert_exists and key_exists and ca_exists else ' 部分配置需要检查'}")
    
except Exception as e:
    print(f"\n 验证失败: {e}")
    import traceback
    traceback.print_exc()
