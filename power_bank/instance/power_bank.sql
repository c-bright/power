
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱',
    address VARCHAR(255) NOT NULL DEFAULT '' COMMENT '区块链公钥地址',
    balance DECIMAL(20, 8) NOT NULL DEFAULT 0 COMMENT '账户余额',
    remark TEXT COMMENT '文本信息（备注）',
    sync_status tinyint DEFAULT '0',
    tx_hash varchar(100) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_address (address)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS admin (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '管理员ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    address VARCHAR(255) NOT NULL DEFAULT '' COMMENT '区块链公钥地址',
    password VARCHAR(255) NOT NULL DEFAULT '123456' COMMENT '密码',
    can_manage_info TINYINT(1) DEFAULT 0 COMMENT '是否有information表权限(1:有, 0:无)',
    can_manage_rules TINYINT(1) DEFAULT 0 COMMENT '是否有billing_rules表权限',
    can_manage_feedback TINYINT(1) DEFAULT 0 COMMENT '是否有feedback表权限',
    sync_status tinyint DEFAULT '0',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    tx_hash varchar(100) DEFAULT NULL

) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE  IF NOT EXISTS Information (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '充电宝ID',
    location VARCHAR(100) NOT NULL COMMENT '设备位置',
    status ENUM('online', 'offline', 'repair') NOT NULL DEFAULT 'online' COMMENT '设备状态',
    battery_level INT NOT NULL COMMENT '电量百分比(0-100)',
    capacity ENUM('small', 'medium', 'large') NOT NULL COMMENT '容量规格',
    function_type ENUM('fast', 'normal') NOT NULL COMMENT '功能类型',
    created_at timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '建表时间',
    username VARCHAR(50) NULL UNIQUE DEFAULT NULL COMMENT '用户名',
    order_no VARCHAR(32) NULL UNIQUE DEFAULT NULL COMMENT '订单编号',
    sync_status tinyint DEFAULT '0',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    tx_hash varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='充电宝信息表';

CREATE TABLE IF NOT EXISTS rent_record (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '借还记录ID',
    order_no VARCHAR(32) NOT NULL COMMENT '订单编号',
    location VARCHAR(100) NOT NULL COMMENT '借出位置',
    capacity ENUM('small', 'medium', 'large') NOT NULL COMMENT '规格',
    function_type ENUM('fast', 'normal') NOT NULL COMMENT '功能类型',
    rent_time DATETIME NOT NULL COMMENT '借出时间',
    return_time DATETIME COMMENT '归还时间',
    cost DECIMAL(10,2) DEFAULT 0.00 COMMENT '使用费用',
    status ENUM('renting', 'returned')
           NOT NULL DEFAULT 'renting' COMMENT '记录状态',
    username VARCHAR(50) NULL DEFAULT NULL COMMENT '用户名',
    sync_status tinyint DEFAULT '0',
    tx_hash varchar(100) DEFAULT NULL,
    INDEX idx_order_no (order_no),
    INDEX idx_status (status),
    INDEX idx_rent_time (rent_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='充电宝借还记录表';


CREATE TABLE IF NOT EXISTS billing_rules (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    free_minutes INT NOT NULL DEFAULT 5 COMMENT '免费时长(分钟)',
    hourly_price DECIMAL(10, 2) NOT NULL DEFAULT 3.00 COMMENT '每小时单价(元)',
    daily_max DECIMAL(10, 2) NOT NULL DEFAULT 30.00 COMMENT '当日封顶(元)',
    deposit DECIMAL(10, 2) NOT NULL DEFAULT 99.00 COMMENT '押金金额(元)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间',
    sync_status tinyint DEFAULT '0',
    tx_hash varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='计费标准配置表';

CREATE TABLE IF NOT EXISTS feedback (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_no VARCHAR(32) NOT NULL COMMENT '关联订单号',
    username VARCHAR(50) NOT NULL COMMENT '提交用户',
    content TEXT COMMENT '反馈内容',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'processed') DEFAULT 'pending' COMMENT '处理状态',
    Reply  TEXT COMMENT '理员处理回复',
    sync_status tinyint DEFAULT '0',
    tx_hash varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

