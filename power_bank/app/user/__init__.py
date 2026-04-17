# import pymysql
# import random
# from datetime import datetime, timedelta
#
# # 数据库连接配置
# db_config = {
#     "host": "localhost",
#     "user": "root",
#     "password": "your_password",  # 请替换为实际密码
#     "database": "power",
#     "charset": "utf8mb4"
# }
#
#
# def insert_data_without_blockchain_fields():
#     conn = pymysql.connect(**db_config)
#     cursor = conn.cursor()
#
#     locations = ['北京', '上海', '广州', '深圳', '杭州', '武汉']
#
#     try:
#         for i in range(1, 31):
#             order_no = f"ORD20251226{i:04d}"
#             # 随机生成借还时间
#             r_time = datetime.now() - timedelta(days=random.randint(1, 10))
#             ret_time = r_time + timedelta(hours=random.randint(1, 3))
#
#             # 注意：此处 SQL 字段列表中不包含 sync_status 和 tx_hash
#             sql = """
#             INSERT INTO rent_record
#             (order_no, location, capacity, function_type, rent_time, return_time, cost, status, username)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """
#
#             params = (
#                 order_no,
#                 random.choice(locations),
#                 'medium',
#                 'fast',
#                 r_time,
#                 ret_time,
#                 random.randint(3, 15),
#                 'returned',
#                 '孙沐辰'
#             )
#
#             cursor.execute(sql, params)
#
#         conn.commit()
#         print("成功插入30条数据，sync_status 和 tx_hash 已按要求留空。")
#     except Exception as e:
#         conn.rollback()
#         print(f"执行失败: {e}")
#     finally:
#         conn.close()
#
#
# if __name__ == "__main__":
#     insert_data_without_blockchain_fields()
