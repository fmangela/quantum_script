import re


def tf_filename_compliant(filename: str) -> bool:
    """
    检查给定的文件名是否符合以下规则：\n
     - 仅包含字母（不区分大小写）、数字、下划线（_）和连字符（-）\n
     - 不以点（.）开头\n
     - 不包含连续的点（..）\n
     - 长度在1到255个字符之间（包括1和255个）
    :param filename: 文件名
    :return: bool值
    """

    # 长度校验
    if len(filename) < 1 or len(filename) > 255:
        return False

    # 字符校验
    pattern = r'^[a-zA-Z0-9_\-.]*$'
    if not re.match(pattern, filename):
        return False

    # 首部.字符校验
    if filename.startswith('.'):
        return False

    # 首部..字符校验
    if '..' in filename:
        return False

    # 所有校验都通过，返回
    return True