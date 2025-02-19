"""
读取配置文件模块
详细参数需要每个模块自己获取
"""
import configparser
import os



class FileConfigLoader(object):
    """
    配置文件加载器
    """
    def __init__(self, file_name: str, ROOTPATH: str) -> None:
        """
        初始化配置文件加载器
        :param file_name: 配置文件名称
        """
        self.file_name = file_name
        self.ROOTPATH = ROOTPATH
        # 起配置文件对象
        self.config = configparser.ConfigParser()
        # 获取config文件路径
        self.config_path = self.__load_path(self.file_name)
        if self.config_path is None:
            raise Exception(f'项目根目录的{file_name}配置文件不存在')
        # 不会占用文件
        self.config.read(self.config_path, encoding='utf-8')

    def __load_path(self, file_name: str='config.ini'):
        """
        读取配置文件路径，如果没有，则搜索项目
        :param file_name:配置文件名称
        :return:对应的路径
        """
        # 读取当前程序文件所在目录
        # this_script_dir = os.path.dirname(os.path.abspath(__file__))
        this_script_dir = self.ROOTPATH
        # 拼接默认的目录，默认的配置文件应该在上一层目录下
        config_file_path = os.path.join(this_script_dir, f'../{file_name}')
        if os.path.isfile(config_file_path):
            return config_file_path
        else:
            parent_dir = os.path.dirname(this_script_dir)
            for root, dirs, files in os.walk(parent_dir):
                if file_name in files:
                    return os.path.join(root, file_name)
            return None

    def get(self, section: str, key: str) -> str:
        """
        获取配置文件内容
        :param section: 配置文件段落
        :param key: 配置文件键
        :return: 配置文件内容，字符串
        """
        return self.config.get(section, key)

    def getboolean(self, section: str, key: str) -> bool:
        """
        获取配置文件内容
        :param section: 配置文件段落
        :param key: 配置文件键
        :return: 配置文件内容，布尔值
        """
        return self.config.getboolean(section, key)


if __name__ == '__main__':
    # 测试代码
    loader = FileConfigLoader('config.ini', '.')
    