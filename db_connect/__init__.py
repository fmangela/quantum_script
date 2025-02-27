# 首先读取配置文件查看用的是什么数据库连接
from config import config_
if config_.getboolean('postgresql', 'enable'):
    from pg_db_operator import PgDbOperator
    pg = PgDbOperator()




