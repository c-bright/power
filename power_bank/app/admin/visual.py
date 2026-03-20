# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

from app.extensions import get_db

visual_manage_bp = Blueprint('visual_manage_api', __name__)


@visual_manage_bp.route('/api/admin/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    metrics = {
        "totalRevenue": 0, "totalRevenueGrowth": 0,
        "topLocation": "无数据", "topLocationValue": 0,
        "totalOrders": 0, "totalOrdersGrowth": 0,
        "avgUsageTime": 0, "avgUsageTimeGrowth": 0
    }
    charts = {
        "dates": [],
        "revenueTrend": [],
        "orderCounts": [],
        "locationData": []
    }

    try:
        db = get_db()
        start_date = request.args.get('start')
        end_date = request.args.get('end')

        # 构建日期过滤 SQL
        where_clause = ""
        params = []
        if start_date and end_date:
            where_clause = " WHERE rent_time BETWEEN %s AND %s "
            params = [f"{start_date} 00:00:00", f"{end_date} 23:59:59"]

        # 2. 计算核心指标 (营收、订单量、平均时长)
        sql_summary = f"""
            SELECT 
                SUM(cost) as total_revenue, 
                COUNT(*) as total_orders,
                AVG(TIMESTAMPDIFF(MINUTE, rent_time, return_time)) as avg_minutes
            FROM rent_record 
            {where_clause}
        """
        db.execute(sql_summary, params)
        summary = db.fetchone()

        # 3. 统计“设备使用率最高地区” (取订单数最多的地区)
        sql_top_loc = f"""
            SELECT location, COUNT(*) as usage_count 
            FROM rent_record 
            {where_clause} 
            GROUP BY location 
            ORDER BY usage_count DESC LIMIT 1
        """
        db.execute(sql_top_loc, params)
        top_res = db.fetchone()

        metrics.update({
            "totalRevenue": float(summary['total_revenue'] or 0),
            "totalRevenueGrowth": 15.2,  # 模拟环比
            "topLocation": top_res['location'] if top_res else "无数据",
            "topLocationValue": top_res['usage_count'] if top_res else 0,
            "totalOrders": summary['total_orders'] or 0,
            "totalOrdersGrowth": 8.4,
            "avgUsageTime": round(float(summary['avg_minutes'] or 0), 1),
            "avgUsageTimeGrowth": -2.1
        })

        # 4. 趋势统计 (近7日或选定范围)
        # 🚩 注意：DATE_FORMAT 中的 % 必须写成 %% 以防止 Python 格式化报错
        trend_where = where_clause if start_date else " WHERE rent_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) "
        trend_params = params if start_date else []

        sql_trend = f"""
            SELECT DATE_FORMAT(rent_time, '%%m-%%d') as d, SUM(cost) as rev, COUNT(*) as ord
            FROM rent_record {trend_where}
            GROUP BY d ORDER BY d ASC
        """
        db.execute(sql_trend, trend_params)
        trend_res = db.fetchall()
        charts["dates"] = [r['d'] for r in trend_res]
        charts["revenueTrend"] = [float(r['rev']) for r in trend_res]
        charts["orderCounts"] = [r['ord'] for r in trend_res]

        # 5. 地区分布统计 (用于饼图)
        sql_loc_dist = f"SELECT location as name, COUNT(*) as value FROM rent_record {where_clause} GROUP BY location"
        db.execute(sql_loc_dist, params)
        charts["locationData"] = db.fetchall()

        return jsonify({"success": True, "metrics": metrics, "charts": charts})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e), "metrics": metrics, "charts": charts}), 500

