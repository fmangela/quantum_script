import os,sys

def executable_file_path() -> str:
    """
    1执行脚本的那个文件的路径\n
    2可执行程序exe文件的路径\n
    如果后期项目需要打包成可执行程序文件（即exe文件），则返回exe文件所在的路径
    :return: 被执行文件的绝对路径
    """
    return os.path.dirname(sys.argv[0])

def project_path() -> str:
    """
    1执行的脚本或exe正好是在根目录下\n
    获取项目根目录
    :return: 项目根目录
    """
    # 尝试获取PyInstaller的临时运行目录
    try:
        # PyInstaller创建了一个临时文件夹并把路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        # 如果不是由PyInstaller启动，则根据当前文件位置计算项目根目录
        base_path = os.path.abspath(os.path.dirname(__file__))
    return base_path

if __name__ == '__main__':
    # 测试
    print(project_path())
