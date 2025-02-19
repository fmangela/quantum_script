from quantum.file_rw_io.project_position import executable_file_path,project_path
from quantum.config.file_config_loader import FileConfigLoader


# 执行文件的目录（可执行文件exe或者main.py所在的目录）
ROOTPATH = executable_file_path()
# 项目的根目录（main.py所在的目录）
PROJECT_PATH = project_path()
"""
1 请将config.ini.dist配置好后，复制并更改后缀名称
2 使用方法CONFIG_.get('[session]', 'key')
"""
CONFIG_ = FileConfigLoader('config.ini', ROOTPATH)


if __name__ == '__main__':
    print(CONFIG_.get('session', 'key'))
    pass
