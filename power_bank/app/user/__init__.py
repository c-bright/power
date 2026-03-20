# 示例脚本：用于插入 rent_record 模拟数据。
# 如需使用，请先将数据库连接参数改为本地配置。
#
# import os
# import pymysql
# import random
# from datetime import datetime, timedelta
#
# db_config = {
#     "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
#     "user": os.environ.get("MYSQL_USER", "root"),
#     "password": os.environ.get("MYSQL_PASSWORD", "your_password"),
#     "database": os.environ.get("MYSQL_DATABASE", "power"),
#     "charset": "utf8mb4"
# }
#
# def insert_data_without_blockchain_fields():
#     conn = pymysql.connect(**db_config)
#     cursor = conn.cursor()
#     locations = ["北京", "上海", "广州", "深圳", "杭州", "武汉"]
#
#     try:
#         for i in range(1, 31):
#             order_no = f"ORD20251226{i:04d}"
#             r_time = datetime.now() - timedelta(days=random.randint(1, 10))
#             ret_time = r_time + timedelta(hours=random.randint(1, 3))
#             sql = """
#             INSERT INTO rent_record
#             (order_no, location, capacity, function_type, rent_time, return_time, cost, status, username)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """
#             params = (
#                 order_no,
#                 random.choice(locations),
#                 "medium",
#                 "fast",
#                 r_time,
#                 ret_time,
#                 random.randint(3, 15),
#                 "returned",
#                 "sample_user"
#             )
#             cursor.execute(sql, params)
#
#         conn.commit()
#         print("成功插入模拟数据。")
#     except Exception as e:
#         conn.rollback()
#         print(f"执行失败: {e}")
#     finally:
#         conn.close()
#
# if __name__ == "__main__":
#     insert_data_without_blockchain_fields()
