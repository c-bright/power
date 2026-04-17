# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from datetime import datetime
import traceback
from decimal import Decimal

from app.extensions import get_db
from app.auth.decorators import require_auth

dispute_manage_bp = Blueprint('dispute_manage_api', __name__)


@dispute_manage_bp.route('/api/admin/feedback', methods=['GET'])
@require_auth(roles=["admin"])
def get_all_feedback():
    try:
        db = get_db()
        sql = """
            SELECT id, order_no, username, content, created_at, status, reply 
            FROM feedback 
            ORDER BY created_at DESC
        """
        db.execute(sql)
        results = db.fetchall()

        feedback_list = []
        for row in results:
            raw_time = row.get('created_at')

            feedback_list.append({
                # --- 表格显示字段 (与数据库完全对应) ---
                "id": row.get('id'),
                "order_no": row.get('order_no') or '-',
                "username": row.get('username') or '匿名',
                "content": row.get('content') or '无描述',
                "created_at": raw_time.strftime('%Y-%m-%d %H:%M:%S') if raw_time else '-',
                "status": row.get('status') or 'pending',
                "priority": "normal",  # 默认优先级
                "reply": row.get('reply') or '待处理',
            })

        return jsonify({"success": True, "data": feedback_list})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"查询出错: {str(e)}"}), 500


@dispute_manage_bp.route('/api/admin/rent_detail', methods=['GET'])
@require_auth(roles=["admin"])
def get_rent_detail():
    try:
        db = get_db()
        order_no = request.args.get('order_no', '').strip()
        username = request.args.get('username', '').strip()
        #  修正：使用更健壮的查询
        sql = """
            SELECT location, capacity, function_type, rent_time, return_time, cost
            FROM rent_record 
            WHERE order_no = %s AND username = %s
            LIMIT 1
        """
        db.execute(sql, (order_no, username))
        row = db.fetchone()

        if row:
            #  关键：必须确保返回的 Key 名与 Vue 模板中的 {{ activeTicket.xxx }} 一致
            return jsonify({
                "success": True,
                "data": {
                    "location": row.get('location') or '未知地点',
                    "capacity": row.get('capacity') or '-',
                    "function_type": row.get('function_type') or '-',
                    "rent_time": str(row.get('rent_time')) if row.get('rent_time') else '-',
                    "return_time": str(row.get('return_time')) if row.get('return_time') else '-',
                    "cost": float(row.get('cost')) if row.get('cost') else 0.0
                }
            })
        else:
            # 如果没查到数据，返回具体错误
            return jsonify({"success": False, "message": "rent_record 表中无匹配记录"})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@dispute_manage_bp.route('/api/admin/feedback/process', methods=['POST'])
@require_auth(roles=["admin"])
def process_feedback():
    try:
        db = get_db()
        data = request.json
        feedback_id = data.get('id')
        reply_content = data.get('remark')  # 获取前端传来的处理备注

        if not feedback_id or not reply_content:
            return jsonify({"success": False, "message": "参数完整性检查失败"}), 400

        #  更新数据库：将内容写入 reply 字段，并将 status 改为 'processed'
        sql = """
            UPDATE feedback 
            SET reply = %s, status = 'processed', created_at = NOW() 
            WHERE id = %s
        """
        # 注意：这里假设你使用的是 pymysql 或类似的 db 对象
        db.execute(sql, (reply_content, feedback_id))

        return jsonify({"success": True, "message": "处理成功"})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
