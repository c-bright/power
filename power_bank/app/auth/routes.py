# -*- coding: utf-8 -*-
"""认证相关：注册、登录。"""
import hashlib
import os
import random
from itertools import product

import pymysql
from flask import Blueprint, request, jsonify, current_app

from app.extensions import get_db
from app.auth.token_service import create_access_token

auth_bp = Blueprint('auth', __name__)


def _create_name_generator():
    surnames = ["赵", "钱", "孙", "李", "周", "吴", "郑", "王", "冯", "陈",
                "沈", "韩", "杨", "朱", "秦", "尤", "许", "何", "吕", "张"]
    first_names = ["梓轩", "浩然", "语嫣", "若冰", "天佑", "子涵", "雨泽", "墨染",
                   "思源", "梦琪", "佳怡", "博文", "志强", "晓彤", "艺涵", "俊杰",
                   "瑞希", "欣怡", "泽洋", "沐辰"]
    all_names = [f"{s}{f}" for s, f in product(surnames, first_names)]
    random.shuffle(all_names)
    for name in all_names:
        yield name


_name_gen = _create_name_generator()

def _md5_hex(value: str) -> str:
    return hashlib.md5((value or "").encode("utf-8")).hexdigest()


def _verify_password(plain: str, stored: str):
    """
    Return (ok, needs_upgrade_to_md5).
    Backward compatible with existing plaintext passwords.
    """
    if stored is None:
        return False, False
    if stored == plain:
        return True, True
    if stored == _md5_hex(plain):
        return True, False
    return False, False


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    注册接口
    JSON: {"username": "...", "password": "...", "email": "..."}
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"message": "请求格式错误"}), 400

    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    if not username or not password:
        return jsonify({"message": "用户名或密码不能为空"}), 400

    try:
        db = get_db()
        new_chinese_name = next(_name_gen)
        sql = "INSERT INTO users (username, password, email, address, created_at) VALUES (%s, %s, %s, %s, NOW())"
        db.execute(sql, (new_chinese_name, _md5_hex(password), email, username))
        return jsonify({"message": "注册成功"}), 201
    except pymysql.err.IntegrityError:
        return jsonify({"message": "用户名已存在"}), 409
    except Exception as e:
        return jsonify({"message": f"服务器错误: {e}"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    登录接口
    JSON: {"role": "...", "username": "...", "password": "..."}
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"message": "请求格式错误"}), 400

    role = data.get("role")
    username = data.get("username")
    password = data.get("password")

    if not all([role, username, password]):
        return jsonify({"message": "用户名或密码不能为空"}), 400
    if role not in ["users", "admin", "sysadmin"]:
        return jsonify({"message": "角色不存在"}), 400

    try:
        db = get_db()
        if role == "sysadmin":
            pword = "123456"
            addr = current_app.config.get('BANK_DATA')
            if addr == username and pword == password:
                return jsonify({
                    "status": "jump",
                    "type": "WEBASE_JUMP",
                    "message": "系统管理员核验成功，正在跳转至 WeBASE-Front...",
                    "redirect_url": os.environ.get("WEBASE_FRONT_URL", "http://127.0.0.1:5002/WeBASE-Front/#/home")
                }), 200

        elif role == "admin":
            sql = "SELECT id, username, address, password, can_manage_info, can_manage_rules, can_manage_feedback FROM admin WHERE address = %s"
            db.execute(sql, (username,))
            user = db.fetchone()
            if not user:
                return jsonify({"message": "用户名或密码错误"}), 401
            ok, needs_upgrade = _verify_password(password, user.get("password"))
            if not ok:
                return jsonify({"message": "用户名或密码错误"}), 401
            if needs_upgrade:
                db.execute("UPDATE admin SET password = %s WHERE id = %s", (_md5_hex(password), user["id"]))
            token = create_access_token({
                "role": "admin",
                "user_id": user["id"],
                "username": user["username"],
                "address": user["address"],
            })
            return jsonify({
                "message": "登录成功",
                "token": token,
                "expires_in": int(current_app.config.get("ACCESS_TOKEN_EXPIRES", 1800)),
                "user_id": user["id"],
                "username": user["username"],
                "address": user["address"],
                "permissions": {
                    "info": user["can_manage_info"],
                    "rules": user["can_manage_rules"],
                    "feedback": user["can_manage_feedback"]
                }
            }), 200

        else:
            sql = "SELECT id, username, password, email, balance, remark FROM users WHERE address = %s"
            db.execute(sql, (username,))
            user = db.fetchone()
            if not user:
                return jsonify({"message": "用户名或密码错误"}), 401
            ok, needs_upgrade = _verify_password(password, user.get("password"))
            if not ok:
                return jsonify({"message": "用户名或密码错误"}), 401
            if needs_upgrade:
                db.execute("UPDATE users SET password = %s WHERE id = %s", (_md5_hex(password), user["id"]))
            token = create_access_token({
                "role": "users",
                "user_id": user["id"],
                "username": user["username"],
                "address": username,
            })
            return jsonify({
                "message": "登录成功",
                "token": token,
                "expires_in": int(current_app.config.get("ACCESS_TOKEN_EXPIRES", 1800)),
                "user_id": user["id"],
                "username": user["username"],
                "email": user.get("email", ""),
                "balance": float(user.get("balance", 0.0)),
                "remark": user.get("remark", "")
            }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"message": f"服务器错误: {e}"}), 500
