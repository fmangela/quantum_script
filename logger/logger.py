import logging
from logging import StreamHandler
from logging.handlers import TimedRotatingFileHandler
from file_rw_io.file_name import tf_filename_compliant
import os


def set_handler_level(handler: logging.Handler, level: str) -> None:
    """
    设置日志处理器的日志级别
    :param handler: 日志处理器
    :param level: 日志级别
    :return: None
    """
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    handler.setLevel(level_map.get(level, logging.DEBUG))


def setup_logger(name: str, config) -> logging.Logger:
    """
    初始化设置logger，包括命令行窗口显示配置，记录文件配置
    :param name: 日志记录器名字
    :return: 日志记录器
    """
    # 创建一个logger实例
    logger = logging.getLogger(name)
    # 设置最低日志级别为DEBUG
    logger.setLevel(logging.DEBUG)

    # 读取配置文件
    # config = FileConfigLoader('global_config.ini')

    # 创建一个控制台日志处理器，只显示 console_log_level 及以上级别的日志
    console_handler = StreamHandler()

    # 设置 console_handler 的日志级别
    console_log_level = config.get('log', 'console_log_level')
    set_handler_level(console_handler, console_log_level)

    # 输出格式，这里就同一了，不更改了，把时间，信息等级，文件地址，文件名，行号，日志内容都展示出来
    custom_format = '%(asctime)s.%(msecs)03d | %(levelname)s | %(pathname)s | %(filename)s:%(lineno)d | %(message)s'

    console_formatter = logging.Formatter(custom_format, datefmt='%Y-%m-%d %H:%M:%S')
    # 设置 console_handler 的格式器
    console_handler.setFormatter(console_formatter)
    # 将 console_handler 添加到 logger
    logger.addHandler(console_handler)

    # 读取文件目录
    log_path = config.get('log', 'log_path')
    if log_path == '':
        # 如果配置文件中没有设定log文档的目录
        # 获取项目根目录
        project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')  # 这个代码决定了log的包不能动位置
        logs_dir = os.path.join(project_root, 'logs')
        # 如果文件夹不存在，建一个
        if not os.path.exists(logs_dir):
            try:
                os.makedirs(logs_dir)
            except OSError as e:
                raise Exception(f'无法创建日志目录：{logs_dir}，错误信息：{e}')
    else:
        # 使用配置文件中提供的log_path
        logs_dir = log_path
        # 检查提供的log_path是否存在且为目录
        if not os.path.isdir(logs_dir):
            os.makedirs(logs_dir)
        if not os.access(logs_dir, os.W_OK):
            raise Exception(f'指定的日志目录不可写：{logs_dir}')

    # log文件名
    log_file_name = config.get('log', 'log_file_name')
    if log_file_name:
        if not tf_filename_compliant(log_file_name):
            raise Exception(f'日志文件名不符合要求：{log_file_name}')
    else:
        log_file_name = 'app.log'

    # 配置log文件切换时间
    log_switch_time = config.get('log', 'log_switch_time')
    # 配置log文件保留个数
    log_backup_count = config.get('log', 'log_backup_count')
    # 配置编码格式
    log_encoding = config.get('log', 'log_encoding')

    # 创建一个文件日志处理器
    file_handler = TimedRotatingFileHandler(
        os.path.join(logs_dir, log_file_name),
        when=log_switch_time,
        backupCount=int(log_backup_count),
        encoding=log_encoding
    )

    # 设置 file_handler 的日志级别为 DEBUG
    file_log_level = config.get('log', 'file_log_level')
    set_handler_level(file_handler, file_log_level)

    # 输出格式
    file_formatter = logging.Formatter(custom_format, datefmt='%Y-%m-%d %H:%M:%S')
    # 设置 file_handler 的格式器
    file_handler.setFormatter(file_formatter)
    # 将 file_handler 添加到 logger
    logger.addHandler(file_handler)

    return logger



