from quantum.config import config_
from dingding import Dingding

if config_.getboolean('MessagePush', 'is_enable'):
    # 是否钉钉消息推送开启
    if config_.getboolean('DingDing', 'enable'):
        dingding_ = Dingding()

else:
    dingding_ = None