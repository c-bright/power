# -*- coding: utf-8 -*-

# [network] 配置网络连接信息
[network]
# 配置连接的节点，支持多个节点，用逗号分隔
peers=192.168.211.133:20200

# 连接超时时间，单位秒，默认为10秒
timeout=10

# [certificate] 配置证书信息
[certificate]
# 采用channel协议时，需要设置sdk证书
channel_node_cert = "bin\\sdk.crt"

# 采用channel协议时，需要设置sdk私钥
channel_node_key = "bin\\sdk.key"

# [chain] 配置链信息
[chain]
# 链ID，默认为1
chain_id=1

# 群组ID，默认为1
group_id=1

# [account] 配置账户信息
[account]
# 账户私钥文件路径
keyfile = "bin\\sdk.key"

# 账户私钥文件密码，默认为空
password = ""

# [crypto] 配置加密信息
[crypto]
# 国密开关，默认为false，设置为true时使用国密算法
sm_crypto=false

# [log] 配置日志信息
[log]
# 日志级别，支持debug, info, warning, error, critical
log_level=INFO

