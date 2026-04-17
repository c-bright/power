# -*- coding: utf-8 -*-
"""应用配置：从 instance 目录加载 config.ini，并定义配置类。"""
import os
import configparser

class BaseConfig:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'power-bank-dev-secret'
    INSTANCE_PATH = None  # 由 create_app 设置
    ACCESS_TOKEN_EXPIRES = int(os.environ.get("ACCESS_TOKEN_EXPIRES", "1800"))  # seconds
    ACCESS_TOKEN_SALT = os.environ.get("ACCESS_TOKEN_SALT") or "power-bank-access-token"

class DevelopmentConfig(BaseConfig):
    """开发环境"""
    DEBUG = True
    ENV = 'development'


class ProductionConfig(BaseConfig):
    """生产环境"""
    DEBUG = False
    ENV = 'production'


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}


def load_instance_config(app):
    """
    从 instance/config.ini 加载 MySQL 等配置到 app.config。
    若文件不存在则使用环境变量或默认值。
    """
    config_path = os.path.join(app.instance_path, 'config.ini')
    app.config.setdefault('MYSQL_HOST', 'localhost')
    app.config.setdefault('MYSQL_PORT', 3306)
    app.config.setdefault('MYSQL_USER', 'root')
    app.config.setdefault('MYSQL_PASSWORD', '')
    app.config.setdefault('MYSQL_DATABASE', 'power')
    app.config.setdefault('MYSQL_AUTOCOMMIT', True)
    app.config.setdefault('SQL_FILE', os.path.join(app.instance_path, 'power_bank.sql'))

    if os.path.isfile(config_path):
        cf = configparser.ConfigParser()
        cf.read(config_path, encoding='utf-8')
        if cf.has_section('mysql_data'):
            app.config['MYSQL_HOST'] = cf.get('mysql_data', 'host', fallback=app.config['MYSQL_HOST'])
            app.config['MYSQL_PORT'] = cf.getint('mysql_data', 'port', fallback=app.config['MYSQL_PORT'])
            app.config['MYSQL_USER'] = cf.get('mysql_data', 'user', fallback=app.config['MYSQL_USER'])
            app.config['MYSQL_PASSWORD'] = cf.get('mysql_data', 'password', fallback=app.config['MYSQL_PASSWORD'])
            app.config['MYSQL_DATABASE'] = cf.get('mysql_data', 'database', fallback=app.config['MYSQL_DATABASE'])
            app.config['MYSQL_AUTOCOMMIT'] = cf.getboolean('mysql_data', 'autocommit', fallback=True)
    return app
