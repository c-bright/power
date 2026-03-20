# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
import traceback
from datetime import datetime
import math

from app.extensions import get_db

user_rent_bp = Blueprint('user_rent_api', __name__)


@user_rent_bp.route('/api/powerbanks', methods=['GET'])
def get_powerbank_info():
    """
        获取充电宝信息列表接口
        支持查询参数：location, capacity, function_type
        """
    # 获取查询参数 (Query Parameters)
    location_query = request.args.get('location', '')
    status_query = request.args.get('status', '')
    capacity_query = request.args.get('capacity', '')
    function_type_query = request.args.get('function_type', '')

    try:
        current_page = int(request.args.get('currentPage', 1))
        page_size = int(request.args.get('pageSize', 10))
    except ValueError:
        return jsonify({"message": "分页参数格式错误"}), 400

    try:
        db = get_db()
        # 基础 SQL 语句：查询所有相关字段，只选择在线且电量满足条件的设备
        sql_base = "WHERE 1=1"
        params = []

        if location_query:
            sql_base += " AND location LIKE %s"
            params.append(f"%{location_query}%")

        if status_query:
            sql_base += " AND status = %s"
            params.append(status_query)

        if capacity_query:
            # 假设 capacity 是 ENUM 类型，可以直接匹配
            sql_base += " AND capacity = %s"
            params.append(capacity_query)

        if function_type_query:
            sql_base += " AND function_type = %s"
            params.append(function_type_query)

        sql_count = f"SELECT COUNT(*) AS total_count FROM Information {sql_base}"
        db.execute(sql_count, tuple(params))
        total_count = db.fetchone().get('total_count', 0)

        # 如果总数为 0，直接返回
        if total_count == 0:
            return jsonify({
                "message": "当前区域暂无可用充电宝。",
                "total": 0,
                "data": []
            }), 200

        offset = (current_page - 1) * page_size

        # 主查询语句 (已包含 WHERE 和 ORDER BY)
        sql_data = f"""
                    SELECT id, location, status, battery_level, capacity, function_type,username
                    FROM Information 
                    {sql_base}
                    ORDER BY battery_level DESC
                    LIMIT %s OFFSET %s
                """
        # 将 LIMIT 和 OFFSET 参数添加到 params 列表的末尾
        data_params = params + [page_size, offset]

        db.execute(sql_data, tuple(data_params))

        # 使用 fetchall() 获取当前页符合条件的记录
        powerbanks = db.fetchall()

        # 返回数据列表
        return jsonify({
            "message": "查询成功",
            "total": total_count,  # 返回总记录数
            "data": powerbanks  # 返回当前页的数据
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": f"服务器错误，获取信息失败: {e}"}), 500

@user_rent_bp.route('/api/rent', methods=['POST'])
def rent_powerbank():
    data = request.get_json()
    powerbank_id = data.get('powerbank_id')
    username = data.get('username')
    if not powerbank_id or not username:
        return jsonify({"message": "缺少 powerbank_id 或 username"}), 400
    try:
        db = get_db()
        check_user_sql = "SELECT id FROM information WHERE username = %s"
        db.execute(check_user_sql, (username,))
        existing_rent = db.fetchone()

        if existing_rent:
            return jsonify({
                "success": False,
                "message": f"租借失败：用户 {username} 当前已有正在租借中的充电宝，请先归还后再租借。"
            }), 403  # 403 表示拒绝操作

        # --- B. 获取押金标准和用户余额 ---
        # 1. 获取押金
        db.execute("SELECT deposit FROM billing_rules WHERE id = 1")
        rule_res = db.fetchone()
        deposit = float(rule_res['deposit'])

        # 2. 获取余额
        db.execute("SELECT balance FROM users WHERE username = %s", (username,))
        user_res = db.fetchone()
        if not user_res:
            return jsonify({"success": False, "message": "用户信息不存在"}), 404

        current_balance = float(user_res['balance'])

        # --- C. 余额充足性校验 ---
        if current_balance < deposit:
            return jsonify({
                "success": False,
                "message": f"余额不足！当前余额 ￥{current_balance:.2f}，需押金 ￥{deposit:.2f}"
            }), 402
        new_balance = current_balance - deposit
        update_user_sql = "UPDATE users SET balance = %s, created_at = NOW() WHERE username = %s"
        db.execute(update_user_sql, (new_balance, username))

        # 2. 查找并更新 information 表
        # 逻辑：根据 id 找到记录，将 username 修改为传入的值
        order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        sql = "UPDATE information SET username = %s, order_no = %s, status = 'offline', created_at = NOW() WHERE id = %s"
        affected_rows = db.execute(sql, (username, order_no, powerbank_id))

        # 3. 获取设备详情并写入租借记录
        db.execute("SELECT location, capacity, function_type FROM information WHERE id = %s", (powerbank_id,))
        device = db.fetchone()

        insert_record_sql = """
                    INSERT INTO rent_record (order_no, username, location, capacity, function_type, rent_time, status)
                    VALUES (%s, %s, %s, %s, %s, NOW(), 'renting')
                """
        db.execute(insert_record_sql, (order_no, username, device['location'],
                                       device['capacity'], device['function_type']))

        if affected_rows > 0:
            return jsonify({
                   "success": True,
                  "message": f"租借成功，充电宝 {powerbank_id} 已关联至用户 {username}"
              })
        else:
            return jsonify({"success": False, "message": "未找到对应的充电宝ID"}), 404

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


def _huo_qu(duration, db):
    db.execute(
        "SELECT free_minutes, hourly_price, daily_max, deposit "
        "FROM billing_rules WHERE id = 1"
    )
    res = db.fetchone()

    free_minutes = res['free_minutes']
    hourly_price = float(res['hourly_price'])
    daily_max = float(res['daily_max'])
    deposit = float(res['deposit'])

    # 总分钟数（向上取整）
    minutes = math.ceil(duration.total_seconds() / 60)

    # 免费时长内
    if minutes <= free_minutes:
        return [0, deposit]

    # 计费时长
    days = duration.days
    remaining_seconds = duration.seconds
    hours = math.ceil(remaining_seconds / 3600)

    if days == 0:
        total_cost = hourly_price * hours
    else:
        total_cost = daily_max * days + hourly_price * hours

    # 返回列表
    return [total_cost, deposit]

@user_rent_bp.route('/api/return', methods=['POST'])
def return_powerbank():
    data = request.get_json()
    powerbank_id = data.get('powerbank_id')
    username = data.get('username')  # 这里的 username 用于校验，确保只能归还自己租的

    if not powerbank_id or not username:
        return jsonify({"success": False, "message": "归还参数不完整"}), 400

    try:
        db = get_db()
        get_order_sql = "SELECT order_no FROM information WHERE id = %s"
        db.execute(get_order_sql, (powerbank_id,))
        res = db.fetchone()
        check_sql = f"""
               SELECT rent_time 
               FROM rent_record
               WHERE order_no = %s AND status = 'renting'
           """
        db.execute(check_sql, (res['order_no'],))
        record = db.fetchone()

        if not record:
            return jsonify({"success": False, "message": "未找到进行中的订单"}), 404

        rent_time = record['rent_time']
        return_time = datetime.now()

        # --- 步骤 B: 计算费用
        duration = return_time - rent_time
        total_cost, deposit = _huo_qu(duration, db)

        # --- 步骤 C: 更新 rent_record 表 (结算订单) ---
        update_record_sql = f"""
                   UPDATE rent_record
                   SET return_time = %s, cost = %s, status = 'returned'
                   WHERE order_no = %s
               """
        db.execute(update_record_sql, (return_time, total_cost, res['order_no']))

        update_sql = "UPDATE information SET username = NULL, order_no = NULL, status = 'online', created_at = NOW() WHERE id = %s"
        db.execute(update_sql, (powerbank_id,))
        db.execute("SELECT balance FROM users WHERE username = %s", (username,))
        user_res = db.fetchone()
        if user_res:
            new_balance = float(user_res['balance']) - total_cost + deposit
            db.execute("UPDATE users SET balance = %s, created_at = NOW() WHERE username = %s", (new_balance, username))

        return jsonify({
            "success": True,
            "message": f"归还成功！欢迎下次使用。"
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"服务器内部错误: {str(e)}"}), 500

