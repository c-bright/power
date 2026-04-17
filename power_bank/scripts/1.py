# select * from admin;
# select * from billing_rules;
# select * from feedback;
# select * from information;
# select * from rent_record;
# select * from users;
import pymysql
import random
import os
from datetime import datetime, timedelta

# 数据库连接配置
db_config = {
    "host": "localhost",
    "user": "root",
    "password": os.environ.get("MYSQL_PASSWORD", "your_password"),
    "database": "power",
    "charset": "utf8mb4"
}

# 从 information 表获取的基础属性
locations = ['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉', '西安', '重庆']
capacities = ['small', 'medium', 'large']
function_types = ['fast', 'normal']


def generate_random_time(start_year, end_year):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 20)
    delta = end - start
    random_days = random.randrange(delta.days)
    rent_time = start + timedelta(days=random_days, hours=random.randint(8, 22), minutes=random.randint(0, 59))

    # 随机借用时长 30分钟 到 12小时
    duration_minutes = random.randint(30, 720)
    return_time = rent_time + timedelta(minutes=duration_minutes)

    # 计算费用 (每小时 2 元示例)
    cost = round((duration_minutes / 60) * 2, 2)
    return rent_time, return_time, cost


def insert_mock_data():
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

    try:
        for i in range(1, 1500):
            # 随机选择属性
            loc = random.choice(locations)
            cap = random.choice(capacities)
            func = random.choice(function_types)
            user = f"user_{random.randint(100, 999)}"
            order_no = f"ORD{datetime.now().strftime('%Y%m%d')}{i:04d}"

            # 生成时间
            rent_t, return_t, cost = generate_random_time(2022, 2025)

            sql = """
            INSERT INTO rent_record 
            (order_no, location, capacity, function_type, rent_time, return_time, cost, status, username)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                order_no, loc, cap, func,
                rent_t.strftime('%Y-%m-%d %H:%M:%S'),
                return_t.strftime('%Y-%m-%d %H:%M:%S'),
                cost, 'returned', user
            ))

        conn.commit()
        print("成功插入 300 条模拟数据！")
    except Exception as e:
        conn.rollback()
        print(f"插入失败: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    insert_mock_data()
