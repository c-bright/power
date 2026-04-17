import pymysql

from app.sysadmin import conf as config


SYNC_TABLES = [
    "admin",
    "users",
    "billing_rules",
    "Information",
    "feedback",
    "rent_record",
]


def reset_sync_state(table_name=None):
    conn = pymysql.connect(
        host=config.MYSQL_CONFIG["host"],
        user=config.MYSQL_CONFIG["user"],
        password=config.MYSQL_CONFIG["password"],
        database=config.MYSQL_CONFIG["database"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )
    try:
        with conn.cursor() as cursor:
            tables = [table_name] if table_name else SYNC_TABLES
            for table in tables:
                sql = f"UPDATE {table} SET sync_status = 0, tx_hash = NULL, created_at = NOW()"
                cursor.execute(sql)
        conn.commit()
        return {
            "ok": True,
            "tables": [table_name] if table_name else SYNC_TABLES,
            "message": "sync_status 已重置为 0，tx_hash 已重置为 NULL。",
        }
    except Exception as exc:
        conn.rollback()
        return {
            "ok": False,
            "tables": [table_name] if table_name else SYNC_TABLES,
            "message": str(exc),
        }
    finally:
        conn.close()


if __name__ == "__main__":
    result = reset_sync_state()
    print(result)
