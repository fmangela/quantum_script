


def input_and_validate(validate_func: callable, max_attempts: int = 3) -> str:
    """
    输入并验证\n
    在命令行界面输入内容，并通过该函数记入并返回\n
    :param validate_func: 验证函数，对输入的字符串进行判断是否合规，合规应返回true，不合规应该返回false
    :param max_attempts: 验证次数，默认为3次，3次满了就推出程序
    :return: 输入的内容（字符串）
    """
    for attempt in range(max_attempts):
        input_str = input("请输入：").strip()
        if not input_str:
            print("输入不能为空，请重新输入")
            continue

        try:
            # 验证输入是否合法
            if validate_func(input_str):
                return input_str
            else:
                print("输入错误，请重新输入")
        except TypeError as e:
            print(f"输入错误：{e}，请确保输入格式正确")
        except Exception as e:
            print(f"发生未知错误：{e}，请重新输入")

        if attempt < max_attempts - 1:
            print(f"您还有{max_attempts - attempt -1}次尝试机会")
    print("输入错误次数过多，程序结束")
    raise SystemExit

"""
validate_func在下面添加
"""
