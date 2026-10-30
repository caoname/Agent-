"""
打印日志，方便知道模型正在做什么
"""

import logging
from utils.path_tool import get_abs_path
import os
from datetime import datetime

# 日志保存的根目录
LOG_ROOT = get_abs_path("logs")

# 确保日志的目录存在
os.makedirs(LOG_ROOT, exist_ok=True)

# 日志的配置格式 error  info  debug
DEFAULT_LOG_FORMAT = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)


def get_logger(
        name: str = "agent",  # 给日志取名字，区分不同的模块，可以传进来名字，不传就默认是agent
        console_level: int = logging.INFO,  # 日志的默认级别
        file_level: int = logging.DEBUG,  # 文件级别
        log_file=None,
) -> logging.Logger:  # 返回的是logging.Logger的类对象
    logger = logging.getLogger(name)  # 日志管理器
    logger.setLevel(logging.DEBUG)  # 设置日志级别

    # 避免重复添加handler,因为有很多文件都会调用日志文件，所以就必须提前判断某个日志文件是否已经存在，
    # 存在就直接返回，避免重复添加handler
    if logger.handlers:
        return logger

    # 控制台Handler，在控制台中显示日志信息
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(console_handler)

    # 文件Handler，目的是不仅能在控制台显示日志，还可以记录到文件中，在文件中查看
    if not log_file:  # 日志文件的存放路径
        log_file = os.path.join(LOG_ROOT, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")

    # 根据路径构建文件，并设置文件相关的级别
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(file_handler)

    return logger


# 快速获取日志器
logger = get_logger()


if __name__ == '__main__':
    logger.info("信息日志")
    logger.error("错误日志")
    logger.warning("警告日志")
    logger.debug("调试日志")
