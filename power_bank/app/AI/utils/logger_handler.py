import os
import logging
from datetime import datetime
from app.AI.utils.path_tool import build_path
from logging.handlers import TimedRotatingFileHandler


def get_logger(name="agany"):
    """
    创建并返回 logger
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 防止重复添加 handler
    if logger.handlers:
        return logger

    # 日志目录
    log_dir = build_path("logs")
    os.makedirs(log_dir, exist_ok=True)

    # 日志文件名（按日期）
    log_file = os.path.join(
        log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log"
    )

    # 格式
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )

    # 文件输出
    file_handler = TimedRotatingFileHandler(filename=str(log_file),  when="midnight", interval=1, backupCount=7,encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    # 避免日志重复打印
    logger.propagate = False

    # 添加 handler
    logger.addHandler(file_handler)
    # logger.addHandler(console_handler)

    return logger

logger = get_logger()

if __name__ == "__main__":
    logger = get_logger()

    # logger.debug("这是 DEBUG")
    logger.info("这是 INFO")
    logger.warning("这是 WARNING")
    logger.error("这是 ERROR")
