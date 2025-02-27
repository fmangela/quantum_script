from logger.logger import setup_logger
from config import config_

"""
log日志实例
1 使用方法log.info("记录信息")
2 相关内容详见配置文件
"""

log = setup_logger('main', config_)