# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
import traceback
from datetime import datetime
import math

from app.extensions import get_db

user_rent_history_bp = Blueprint('user_query_api', __name__)


@user_rent_history_bp.route('/api/history', methods=['GET'])
def get_rent_history():
    # 1. 接收前端参数 (对应前端 searchForm)
    order_no = request.args.get("orderNo", "").strip()
    status = request.args.get("status", "")
    start_time = request.args.get("startTime", "")
    end_time = request.args.get("endTime", "")
    username = request.args.get("username", "")
    # 分页参数
    try:
        current_page = int(request.args.get('currentPage', 1))
        page_size = int(request.args.get('pageSize', 10))
    except ValueError:
        return jsonify({"message": "分页参数格式错误"}), 400

    try:
        db = get_db()
        # 构建基础查询条件
        sql_where = "WHERE 1=1 AND username LIKE %s"
        params = [f"%{username}%"]

        # 2. 订单编号模糊查询 (利用 idx_order_no 索引)
        if order_no:
            sql_where += " AND order_no LIKE %s"
            params.append(f"%{order_no}%")

        # 3. 状态筛选映射 (前端: in_progress/completed -> DB: renting/returned)
        status_map = {
            "in_progress": "renting",
            "completed": "returned"
        }
        if status in status_map:
            sql_where += " AND status = %s"
            params.append(status_map[status])

        # 4. 时间范围筛选 (利用 idx_rent_time 索引)
        if start_time and end_time:
            # 清洗 ISO 8601 格式 (2025-12-17T12:00:00.000Z -> 2025-12-17 12:00:00)
            clean_start = start_time.replace("T", " ").split(".")[0].replace("Z", "")
            clean_end = end_time.replace("T", " ").split(".")[0].replace("Z", "")
            sql_where += " AND rent_time BETWEEN %s AND %s"
            params.extend([clean_start, clean_end])

        # 5. 查询总条数
        sql_count = f"SELECT COUNT(*) AS total FROM rent_record {sql_where}"
        db.execute(sql_count, tuple(params))
        total = db.fetchone()["total"]

        if total == 0:
            return jsonify({
                "message": "暂无借还记录",
                "total": 0,
                "data": []
            })

        # 6. 分页查询数据
        offset = (current_page - 1) * page_size
        sql_data = f"""
            SELECT 
                order_no, 
                location, 
                capacity, 
                function_type, 
                rent_time AS borrow_time, 
                return_time, 
                cost, 
                status
            FROM rent_record
            {sql_where}
            ORDER BY rent_time DESC 
            LIMIT %s OFFSET %s
        """

        # 合并查询参数和分页参数
        db.execute(sql_data, tuple(params + [page_size, offset]))
        rows = db.fetchall()

        # 7. 格式化输出给前端
        for row in rows:
            # 将数据库状态转回前端识别的状态码
            row["status"] = "in_progress" if row["status"] == "renting" else "completed"

            # 处理日期格式化（避免 JSON 序列化时报错）
            if row.get("borrow_time"):
                row["borrow_time"] = row["borrow_time"].strftime("%Y-%m-%d %H:%M:%S")
            if row.get("return_time"):
                row["return_time"] = row["return_time"].strftime("%Y-%m-%d %H:%M:%S")

            # 确保费用是浮点数
            row["cost"] = float(row["cost"]) if row["cost"] is not None else 0.0

        return jsonify({
            "message": "查询成功",
            "total": total,
            "data": rows
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": f"服务器内部错误: {str(e)}"}), 500


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

@user_rent_history_bp.route('/api/history', methods=['POST'])
def handle_return_and_settle():
    data = request.get_json()
    # 前端传过来的数据
    order_no = data.get('order_no')
    username = data.get('username')

    if not order_no or not username:
        return jsonify({"success": False, "message": "参数缺失"}), 400

    try:
        db = get_db()
        # --- 步骤 A: 校验并获取借出时间 ---
        check_sql = f"""
        SELECT rent_time 
        FROM rent_record
        WHERE order_no = %s AND status = 'renting'
    """
        db.execute(check_sql, (order_no,))
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
        db.execute(update_record_sql, (return_time, total_cost, order_no))

        # --- 步骤 D: 更新 Information 表 (释放充电宝) ---
        # 将 username 设为 NULL，状态恢复为 online
        update_info_sql = "UPDATE Information SET username = NULL, order_no = NULL, status = 'online', created_at = NOW() WHERE order_no = %s"
        db.execute(update_info_sql, (order_no,))

        db.execute("SELECT balance FROM users WHERE username = %s", (username,))
        user_res = db.fetchone()
        if user_res:
            new_balance = float(user_res['balance']) - total_cost + deposit
            db.execute("UPDATE users SET balance = %s, created_at = NOW() WHERE username = %s", (new_balance, username))

        return jsonify({
            "success": True,
            "message": f"结算成功！费用：￥{total_cost:.2f}",
            "data": {
                "cost": total_cost,
                "return_time": return_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "message": f"服务器结算失败: {str(e)}"}), 500


@user_rent_history_bp.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    order_no = data.get('order_no')
    username = data.get('username')
    content = data.get('content', '').strip() or '用户未填写具体评价'

    if not order_no or not username:
        return jsonify({"success": False, "message": "参数缺失"}), 400

    try:
        db = get_db()
        sql = "INSERT INTO feedback (order_no, username, content, created_at) VALUES (%s, %s, %s, NOW())"
        result = db.execute(sql, (order_no, username, content))


        return jsonify({"success": True, "message": "反馈提交成功！"})

    except Exception as e:
        print(f"数据库操作异常: {str(e)}")  # 这里会打印具体的 SQL 报错
        return jsonify({"success": False, "message": f"提交失败: {str(e)}"}), 500


@user_rent_history_bp.route('/api/notifications', methods=['GET'])
def get_user_notifications():
    # 🚩 优化 1：处理空参数情况，避免后端 SQL 报错
    username = request.args.get('username', '').strip()

    if not username:
        return jsonify({"success": True, "data": []})  # 用户未登录时返回空数组，不报错

    try:
        db = get_db()
        sql = """
            SELECT id, order_no, reply, created_at 
            FROM feedback 
            WHERE username = %s 
              AND reply IS NOT NULL 
              AND reply != '' 
              AND status = 'processed'
            ORDER BY created_at DESC
        """
        db.execute(sql, (username,))
        results = db.fetchall()

        notifications = []
        if not results:
            notifications.append({
                "id": 0,
                "order_no": "SYSTEM",
                "content": "欢迎使用共享充电宝系统！若在使用过程中遇到计费纠纷，请点击反馈。您的反馈处理后将显示在此处。",
                "time": datetime.now().strftime('%Y-%m-%d %H:%M')
            })
        else:
            for row in results:
                # 🚩 优化 3：时间格式化
                # 前端 {{ msg.time }} 渲染字符串更友好，去掉毫秒部分
                raw_time = row.get('created_at')
                formatted_time = "-"
                if isinstance(raw_time, datetime):
                    formatted_time = raw_time.strftime('%Y-%m-%d %H:%M')
                elif raw_time:
                    formatted_time = str(raw_time)[:16]  # 截取到分钟

                notifications.append({
                    "id": row.get('id'),
                    "order_no": row.get('order_no'),
                    # 🚩 优化 4：保持 content 简洁，方便前端在 notification 横幅展示
                    "content": f"订单 {row.get('order_no')} 管理员回复：{row.get('reply')}",
                    "time": formatted_time
                })

        return jsonify({
            "success": True,
            "data": notifications
        })

    except Exception as e:
        import traceback
        traceback.print_exc()  # 在服务端控制台打印具体错误堆栈
        return jsonify({"success": False, "message": "获取通知失败"}), 500
