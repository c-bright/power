# -*- coding: utf-8 -*-
"""璁よ瘉鐩稿叧锛氭敞鍐屻€佺櫥褰曘€?""
import random
from itertools import product

import os
import pymysql
from flask import Blueprint, request, jsonify, current_app

from app.extensions import get_db

auth_bp = Blueprint('auth', __name__)


def _create_name_generator():
    surnames = ["璧?, "閽?, "瀛?, "鏉?, "鍛?, "鍚?, "閮?, "鐜?, "鍐?, "闄?,
                "娌?, "闊?, "鏉?, "鏈?, "绉?, "灏?, "璁?, "浣?, "鍚?, "寮?]
    first_names = ["姊撹僵", "娴╃劧", "璇", "鑻ュ啺", "澶╀綉", "瀛愭兜", "闆ㄦ辰", "澧ㄦ煋",
                   "鎬濇簮", "姊︾惇", "浣虫€?, "鍗氭枃", "蹇楀己", "鏅撳饯", "鑹烘兜", "淇婃澃",
                   "鐟炲笇", "娆ｆ€?, "娉芥磱", "娌愯景"]
    all_names = [f"{s}{f}" for s, f in product(surnames, first_names)]
    random.shuffle(all_names)
    for name in all_names:
        yield name


_name_gen = _create_name_generator()


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    娉ㄥ唽鎺ュ彛
    JSON: {"username": "...", "password": "...", "email": "..."}
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"message": "璇锋眰鏍煎紡閿欒"}), 400

    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    if not username or not password:
        return jsonify({"message": "鐢ㄦ埛鍚嶆垨瀵嗙爜涓嶈兘涓虹┖"}), 400

    try:
        db = get_db()
        new_chinese_name = next(_name_gen)
        sql = "INSERT INTO users (username, password, email, address, created_at) VALUES (%s, %s, %s, %s, NOW())"
        db.execute(sql, (new_chinese_name, password, email, username))
        from app.sysadmin.test.power_user import UserService
        user_api = UserService()
        user_api.create_user(username, new_chinese_name, password, email, 0.00)
        return jsonify({"message": "娉ㄥ唽鎴愬姛"}), 201
    except pymysql.err.IntegrityError:
        return jsonify({"message": "鐢ㄦ埛鍚嶅凡瀛樺湪"}), 409
    except Exception as e:
        return jsonify({"message": f"鏈嶅姟鍣ㄩ敊璇? {e}"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    鐧诲綍鎺ュ彛
    JSON: {"role": "...", "username": "...", "password": "..."}
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"message": "璇锋眰鏍煎紡閿欒"}), 400

    role = data.get("role")
    username = data.get("username")
    password = data.get("password")

    if not all([role, username, password]):
        return jsonify({"message": "鐢ㄦ埛鍚嶆垨瀵嗙爜涓嶈兘涓虹┖"}), 400
    if role not in ["users", "admin", "sysadmin"]:
        return jsonify({"message": "瑙掕壊涓嶅瓨鍦?}), 400

    try:
        db = get_db()
        if role == "sysadmin":
            pword = current_app.config.get("SYSADMIN_PASSWORD", os.environ.get("SYSADMIN_PASSWORD", "change_me"))
            addr = current_app.config.get('BANK_DATA')
            if addr == username and pword == password:
                return jsonify({
                    "status": "jump",
                    "type": "WEBASE_JUMP",
                    "message": "绯荤粺绠＄悊鍛樻牳楠屾垚鍔燂紝姝ｅ湪璺宠浆鑷?WeBASE-Front...",
                    "redirect_url": current_app.config.get("WEBASE_FRONT_URL", os.environ.get("WEBASE_FRONT_URL", "http://127.0.0.1:5002/WeBASE-Front/#/home"))
                }), 200

        elif role == "admin":
            sql = "SELECT id, username, address, password, can_manage_info, can_manage_rules, can_manage_feedback FROM admin WHERE address = %s"
            db.execute(sql, (username,))
            user = db.fetchone()
            if not user:
                return jsonify({"message": "鐢ㄦ埛鍚嶆垨瀵嗙爜閿欒"}), 401
            return jsonify({
                "message": "鐧诲綍鎴愬姛",
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
                return jsonify({"message": "鐢ㄦ埛鍚嶆垨瀵嗙爜閿欒"}), 401
            return jsonify({
                "message": "鐧诲綍鎴愬姛",
                "user_id": user["id"],
                "username": user["username"],
                "email": user.get("email", ""),
                "balance": float(user.get("balance", 0.0)),
                "remark": user.get("remark", "")
            }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"message": f"鏈嶅姟鍣ㄩ敊璇? {e}"}), 500


