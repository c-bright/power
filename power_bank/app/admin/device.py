# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
import traceback
from datetime import datetime

from app.extensions import get_db

device_manage_bp = Blueprint('device_manage_api', __name__)


@device_manage_bp.route('/api/devices', methods=['GET'])
def get_device_list():
    location = request.args.get("location", "").strip()
    status = request.args.get("status", "").strip()
    try:
        current_page = int(request.args.get('currentPage', 1))
        page_size = int(request.args.get('pageSize', 8))
    except ValueError:
        current_page, page_size = 1, 8

    try:
        db = get_db()
        # 构建基础查询条件
        sql_where = "WHERE 1=1"
        params = []

        # 位置模糊查询
        if location:
            sql_where += " AND location LIKE %s"
            params.append(f"%{location}%")

        # 状态精确查询 (online/repair)
        if status:
            sql_where += " AND status = %s"
            params.append(status)

        # 4. 查询总数 (用于前端分页器展示 total)
        sql_count = f"SELECT COUNT(*) AS total FROM information {sql_where}"
        db.execute(sql_count, tuple(params))
        total_res = db.fetchone()
        total = total_res["total"] if total_res else 0

        # 5. 分页查询数据
        offset = (current_page - 1) * page_size
        sql_data = f"""
            SELECT 
                id, 
                location, 
                status, 
                battery_level, 
                capacity, 
                function_type, 
                created_at
            FROM information
            {sql_where}
            ORDER BY id DESC
            LIMIT %s OFFSET %s
        """

        # 合并查询参数和分页参数
        db.execute(sql_data, tuple(params + [page_size, offset]))
        rows = db.fetchall()

        # 6. 格式化输出给前端 (适配 Vue 中的字段名)
        for row in rows:
            # 格式化日期：将 created_at 转换为前端需要的 create_time 字符串
            if row.get("created_at"):
                row["create_time"] = row["created_at"].strftime("%Y-%m-%d %H:%M")
                # 删除原 key 避免冗余
                del row["created_at"]
            else:
                row["create_time"] = ""

        # 7. 返回符合前端逻辑的响应
        return jsonify({
            "code": 200,
            "message": "查询成功",
            "total": total,
            "data": rows
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": f"服务器内部错误: {str(e)}"
        }), 500


@device_manage_bp.route('/api/devices', methods=['POST'])
def create_device():
    try:
        db = get_db()
        data = request.json
        # 准备 SQL，created_at 设为当前时间
        sql = """
            INSERT INTO information 
            (location, status, battery_level, capacity, function_type, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        # 格式化当前时间
        now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        params = (
            data.get('location'),
            data.get('status', 'online'),  # 默认在线
            data.get('battery_level', 100),
            data.get('capacity', 'medium'),
            data.get('function_type', 'normal'),
            now_time
        )

        db.execute(sql, params)
        return jsonify({"code": 200, "message": "创建成功", "data": data})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"code": 500, "message": f"创建失败: {str(e)}"}), 500


@device_manage_bp.route('/api/devices/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    try:
        db = get_db()
        data = request.json
        # 根据 ID 更新指定记录
        sql = """
            UPDATE information 
            SET location=%s, status=%s, battery_level=%s, 
                capacity=%s, function_type=%s, created_at=%s 
            WHERE id=%s
        """
        params = (
            data.get('location'),
            data.get('status'),
            data.get('battery_level'),
            data.get('capacity'),
            data.get('function_type'),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            device_id
        )

        db.execute(sql, params)
        return jsonify({"code": 200, "message": "更新成功", "data": data})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"code": 500, "message": f"更新失败: {str(e)}"}), 500


@device_manage_bp.route('/api/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    try:
        db = get_db()
        sql = "DELETE FROM information WHERE id = %s"
        db.execute(sql, (device_id,))
        return jsonify({"code": 200, "message": "删除成功"})
    except Exception as e:
        return jsonify({"code": 500, "message": f"删除失败: {str(e)}"}), 500
