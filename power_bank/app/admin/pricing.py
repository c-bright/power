# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
import traceback

from app.extensions import get_db

pricing_manage_bp = Blueprint('pricing_manage_api', __name__)


@pricing_manage_bp.route('/api/pricing-rules', methods=['GET'])
def get_pricing_rules():
    try:
        db = get_db()
        db.execute("SELECT free_minutes, hourly_price, daily_max, deposit FROM billing_rules WHERE id = 1")
        res = db.fetchone()
        if res:
            # 转换 Decimal 为 float，确保前端 JS 能正常处理数字
            return jsonify({
                "code": 200,
                "message": "获取成功",
                "data": {
                    "free_minutes": res['free_minutes'],
                    "hourly_price": float(res['hourly_price']),
                    "daily_max": float(res['daily_max']),
                    "deposit": float(res['deposit'])
                }
            })
        else:
            # 数据库没记录，返回 data: None，前端会逻辑自动走默认值
            return jsonify({"code": 200, "data": None, "message": "暂无配置"})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"}), 500


@pricing_manage_bp.route('/api/pricing-rules', methods=['POST'])
def save_pricing_rules():
    try:
        db = get_db()
        data = request.json
        # 使用 ON DUPLICATE KEY UPDATE 确保 ID=1 冲突时执行更新
        sql = """
            INSERT INTO billing_rules (id, free_minutes, hourly_price, daily_max, deposit)
            VALUES (1, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                free_minutes = VALUES(free_minutes),
                hourly_price = VALUES(hourly_price),
                daily_max = VALUES(daily_max),
                deposit = VALUES(deposit)
        """
        params = (
            data.get('free_minutes'),
            data.get('hourly_price'),
            data.get('daily_max'),
            data.get('deposit')
        )

        # 在 autocommit=True 模式下，execute 后数据会立即写入磁盘
        db.execute(sql, params)
        from app.sysadmin.test.test_power_billing import PowerBillingTestClient
        ji_fei = PowerBillingTestClient()
        ji_fei.update_billing_rule(
            data.get('free_minutes'),
            data.get('hourly_price'),
            data.get('daily_max'),
            data.get('deposit')
        )
        return jsonify({"code": 200, "message": "配置已保存"})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"code": 500, "message": f"保存失败: {str(e)}"}), 500
