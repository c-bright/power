import sys
import os
sys.path.insert(0, os.getcwd())

print("Python配置导入测试:")
print("==================")

try:
    from client_config import client_config
    print(" 1. 配置类导入成功")
    
    # 验证关键配置
    print(" 2. 关键配置验证:")
    print(f"   算法类型: {client_config.crypto_type}")
    print(f"   通信协议: {client_config.client_protocol}")
    print(f"   链ID: {client_config.fiscoChainId}")
    print(f"   群组ID: {client_config.groupid}")
    print(f"   节点地址: {client_config.channel_host}:{client_config.channel_port}")
    
    # 检查文件路径
    print(" 3. 文件路径检查:")
    
    # 检查账户文件
    account_paths = [
        client_config.account_keyfile,
        os.path.join(client_config.account_keyfile_path, 'pyaccount.keystore')
    ]
    
    account_found = False
    for path in account_paths:
        if os.path.exists(path):
            print(f"   账户文件:  {path}")
            account_found = True
            break
    
    if not account_found:
        print("   账户文件:  未找到，可能需要创建")
    
    # 检查证书文件
    if client_config.client_protocol == 'channel':
        cert_exists = os.path.exists(client_config.channel_node_cert)
        key_exists = os.path.exists(client_config.channel_node_key)
        ca_exists = os.path.exists(client_config.channel_ca)
        
        cert_mark = "" if cert_exists else ""
        key_mark = "" if key_exists else ""
        ca_mark = "" if ca_exists else ""
        
        print(f"   证书文件: {cert_mark} {client_config.channel_node_cert}")
        print(f"   私钥文件: {key_mark} {client_config.channel_node_key}")
        print(f"   CA证书: {ca_mark} {client_config.channel_ca}")
    
    print("\n 配置验证通过！")
    
except ImportError as e:
    print(f" 导入错误: {e}")
except Exception as e:
    print(f" 其他错误: {e}")
    import traceback
    traceback.print_exc()
