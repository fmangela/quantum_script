"""
钉钉消息推送模块
"""
from config import config_
from logger import log
import requests
import json
import time
import hashlib
import hmac
import base64
import urllib.parse


class Dingding:

    def __init__(self):
        """
        初始化钉钉机器人的时候，读取全局配置文件
        """
        # 尝试获取配置文件中的参数并检验其合法性
        try:
            self._read_config(config_)
        except Exception as e:
            log.error(f"配置文件读取错误: {str(e)}")
            raise

    def _read_config(self, config):
        """
        读取并校验配置项，在对象初始化时被调用
        :param config:为configparser生成的实际对象configparser.ConfigParser()
        :return None
        """
        # 尝试获取配置文件中的参数
        log.info('正在读取钉钉消息推送相关参数配置')

        self.is_enable = config.getboolean('MessagePush', 'is_enable')
        self.is_dingding = config.getboolean('DingDing', 'enable')
        webhook_all = config.get('DingDing', 'webhook')
        self.webhook = webhook_all.split('?')[0]
        self.access_token = webhook_all.split('?')[1].split('=')[1]
        self.keyword = config.get('DingDing', 'keyword')
        self.secret = config.get('DingDing', 'secret')

        # 检验配置项的合法性
        if not self._is_bool(self.is_enable):
            log.error('配置项is_enable的值不是布尔类型')
            raise ValueError('配置项is_enable的值不是布尔类型')
        if not self._is_bool(self.is_dingding):
            log.error('配置项DingDing的值不是布尔类型')
            raise ValueError('配置项DingDing的值不是布尔类型')
        if not self.webhook:
            log.error('未配置钉钉webhook')
            raise ValueError('未配置钉钉webhook')

        if self.keyword:
            log.info('钉钉推送已开启关键字')
        if self.secret:
            log.info('钉钉推送已开启加签')
        log.info('配置文件读取成功')

    @staticmethod
    def _is_bool(value):
        """
        检查变量是否为布尔类型
        :param value:进入的参数，可能是bool值，又可能不是
        :return:如果变量的值为布尔类型则返回True，否则返回False
        """
        try:
            return isinstance(value, bool)
        except AttributeError:
            # 如果不是字符串则返回False
            return False

    @staticmethod
    def _generate_signature(self):
        """
        根据钉钉文档提供的算法生成签名
        """
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign

    def send_message(self, message_text, at_mobiles=None, is_at_all=False):
        """
        发送钉钉群机器人消息
        :param message_text: 消息文本
        :param at_mobiles: 需要@的手机号列表，可选，默认为空列表不@任何人
        :param is_at_all: 是否@所有人，布尔值，默认为False
        :return: 返回HTTP响应对象
        """
        # 先检查是否开启消息推送
        if not self.is_enable:
            log.info('消息推送未开启')
            return None
        # 检查是否开启钉钉消息推送
        if not self.is_dingding:
            log.info('钉钉消息推送未开启')
            return None
        # 处理请求头
        headers = {
            'Content-Type': 'application/json;charset=utf-8'
        }
        # 处理query参数
        params = {
            'access_token': self.access_token
        }
        # 如果开启了加签功能，则添加signature字段
        if self.secret:
            timestamp, sign = self._generate_signature(self)
            params['timestamp'] = timestamp
            params['sign'] = sign
        # 处理消息主体
        message = {
            'msgtype': 'text',
            'text': {
                'content': f"{self.keyword}温馨提示：{message_text}"
            },
        }
        # 如果需要@人员，则添加@字段
        if at_mobiles:
            message['at'] = {
                'atMobiles': at_mobiles,
                'isAtAll': is_at_all
            }

        # 发送request请求
        response = requests.post(self.webhook, data=json.dumps(message), headers=headers, params=params)
        if response.status_code == 200 and response.json()['errcode'] == 0:
            log.info('钉钉消息推送成功')
        else:
            log.warn('钉钉消息推送失败')
        return response
