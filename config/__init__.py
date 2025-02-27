from file_config_loader import FileConfigLoader
from file_rw_io import ROOTPATH

"""
CONFIG_读取配置文件
1 请将config.ini.dist配置好后，复制并更改后缀名称
2 使用方法CONFIG_.get('[session]', 'key')
"""

config_ = FileConfigLoader('config.ini', ROOTPATH)