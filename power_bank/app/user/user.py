# -*- coding: utf-8 -*-
import hashlib
from flask import Blueprint, request, jsonify

from app.extensions import get_db
from app.auth.decorators import require_auth
from flask import g

user_bp = Blueprint('user_api', __name__)


@user_bp.route('/user/update', methods=['POST'])
@require_auth(roles=["users"])
def update_user_details():
    try:
        db = get_db()
        data = request.get_json()
        username = (g.current_user or {}).get("username")
        email = data.get('email')
        remark = data.get('remark')

        sql = "UPDATE users SET email = %s, remark = %s, created_at = NOW() WHERE username = %s"
        affected_rows = db.execute(sql, (email, remark, username))

        if affected_rows == 0:
            return jsonify({"code": 200, "message": "逻辑成功但未找到匹配用户，数据未变"})

        return jsonify({"code": 200, "message": "更新成功"})
    except Exception as e:
        print(f"异常报错: {e}")
        return jsonify({"code": 500, "message": str(e)}), 500

@user_bp.route('/user/recharge', methods=['POST'])
@require_auth(roles=["users"])
def recharge():
    try:
        db = get_db()
        data = request.get_json(silent=True)
        username = (g.current_user or {}).get("username")
        amount = data.get('amount')

        if not username or amount is None:
            return jsonify({"code": 400, "message": "参数不足"}), 400

        sql = "UPDATE users SET balance = balance + %s, created_at = NOW() WHERE username = %s"
        affected_rows = db.execute(sql, (amount, username))

        if affected_rows == 0:
            return jsonify({"code": 404, "message": "未找到匹配用户，充值失败"}), 404

        # 3. 查询充值后的最新余额返回给前端
        query_sql = "SELECT balance FROM users WHERE username = %s"
        db.execute(query_sql, (username,))
        row = db.fetchone()

        new_balance = float(row['balance']) if row else 0.0

        return jsonify({
            "code": 200,
            "message": "充值成功",
            "new_balance": new_balance
        })
    except Exception as e:
        print(f"充值报错: {e}")
        return jsonify({"code": 500, "message": str(e)}), 500


@user_bp.route('/user/update_pwd', methods=['POST'])
@require_auth(roles=["users"])
def update_pwd():
    try:
        db = get_db()
        data = request.get_json(silent=True)
        username = (g.current_user or {}).get("username")
        old_pwd = data.get('old')
        new_pwd = data.get('new')

        if not all([username, old_pwd, new_pwd]):
            return jsonify({"code": 400, "message": "所有字段均为必填"}), 400

        # 1. 验证旧密码是否正确
        query_sql = "SELECT password FROM users WHERE username = %s"
        db.execute(query_sql, (username,))
        user = db.fetchone()

        stored = user.get('password') if isinstance(user, dict) else None
        old_md5 = hashlib.md5((old_pwd or "").encode("utf-8")).hexdigest()
        ok = stored == old_pwd or stored == old_md5
        if not ok:
            return jsonify({"code": 403, "message": "原密码输入错误"}), 403

        # 2. 执行密码更新
        update_sql = "UPDATE users SET password = %s, created_at = NOW() WHERE username = %s"
        new_md5 = hashlib.md5((new_pwd or "").encode("utf-8")).hexdigest()
        db.execute(update_sql, (new_md5, username))

        return jsonify({"code": 200, "message": "密码修改成功"})

    except Exception as e:
        print(f"修改密码报错: {e}")
        return jsonify({"code": 500, "message": str(e)}), 500


@user_bp.route('/user/check_pending', methods=['POST'])
@require_auth(roles=["users"])
def check_pending():
    try:
        db = get_db()
        data = request.get_json(silent=True)
        username = (g.current_user or {}).get("username")

        if not username:
            return jsonify({"code": 400, "message": "参数缺失"}), 400

        # 查询该用户下 return_time 为空或不存在的订单数量
        # 如果 count 为 0，说明所有订单都已结算或根本没有订单
        sql = "SELECT COUNT(*) FROM information WHERE username = %s"
        db.execute(sql, (username,))

        # 使用 fetchone() 获取结果
        res = db.fetchone()

        # 兼容处理：如果返回的是字典则用键名，如果是元组则用下标 [0]
        if isinstance(res, dict):
            count = res.get('COUNT(*)', res.get('count', 0))
        elif isinstance(res, (tuple, list)):
            count = res[0]
        else:
            count = 0

        return jsonify({
            "code": 200,
            "has_pending": count > 0,  # 如果 count > 0，说明有订单没结账
            "count": count
        })

    except Exception as e:
        import traceback
        traceback.print_exc()  # 在终端打印错误详情
        return jsonify({"code": 500, "message": f"后端查询失败: {str(e)}"}), 500

@user_bp.route('/user/delete', methods=['POST'])
@require_auth(roles=["users"])
def delete_account():
    try:
        db = get_db()
        data = request.get_json(silent=True)
        username = (g.current_user or {}).get("username")
        from app.sysadmin.test.test_user_storage import UserStorageTestClient
        service = UserStorageTestClient()
        if not username:
            return jsonify({"code": 400, "message": "缺少用户名"}), 400
        query_sql = "SELECT address FROM users WHERE username = %s"
        db.execute(query_sql, (username,))
        user_record = db.fetchone()
        raw_address = user_record.get('address') if isinstance(user_record, dict) else user_record[0]
        user_address = raw_address.strip()
        service.delete_user(user_address)

        # 执行删除操作
        sql = "DELETE FROM users WHERE username = %s"
        affected_rows = db.execute(sql, (username,))

        if affected_rows == 0:
            return jsonify({"code": 404, "message": "用户不存在或已注销"}), 404

        print(f"用户 {username} 已注销账户")
        return jsonify({"code": 200, "message": "账户已永久注销"})

    except Exception as e:
        print(f"注销报错: {e}")
        return jsonify({"code": 500, "message": str(e)}), 500


