"""
@file:logtofile.py
@time:2019/6/12-14:54
"""
import logging
import random

from constants import LOG_FILE_SAVE_PATH, LOG_DATE_FORMAT


def init_logger(verbose=1, log_name=None):
    # 1.获取日志器 暴露了应用程序代码能直接使用的接口。
    # 如果没有显式的进行创建，则默认创建一个root logger，并应用默认的日志级别(WARN)，
    logger = logging.getLogger(log_name)
    # 设置日志级别
    logger.setLevel(logging.DEBUG if verbose > 1 else logging.INFO)

    # 2.获取处理器 创建一个handler,用于写入日志文件 Formatter默认为%Y-%m-%d %H:%M:%S。
    f_handler = logging.FileHandler(LOG_FILE_SAVE_PATH, encoding='utf-8')
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # formatter = logging.Formatter(LOG_DATE_FORMAT)
    f_handler.setFormatter(formatter)  # 设置格式化器
    f_handler.setLevel(logging.DEBUG)  # 指定日志级别，低于被忽略

    # 3.将处理器添加到日志器中 为Logger实例增加一个处理器,可添加多个handler
    logger.addHandler(f_handler)

    return logger


def get_cookie():  # 构建ua池
    cookies = [
        '_lxsdk_cuid=16b54972c70c8-0ddead0ede0ee9-37c153e-144000-16b54972c70c8; _lxsdk=16b54972c70c8-0ddead0ede0ee9-37c153e-144000-16b54972c70c8; _hc.v=f56d84ff-990f-d4df-8cac-93993402b6be.1560492323; s_ViewType=10; __utma=205923334.1527208716.1560515005.1560515005.1560515005.1; __utmc=205923334; __utmz=205923334.1560515005.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); looyu_id=84b913839d4d4a00377160b29e5bf0965b_51868%3A2; _lxsdk_s=16b563c3110-efa-774-3a8%7C%7C79',
        '_lxsdk_cuid=16b5651483cf-060f4e27830298-37c143e-144000-16b5651483ec8; _lxsdk=16b5651483cf-060f4e27830298-37c143e-144000-16b5651483ec8; _hc.v=d05f3e41-9148-7474-730a-408707b4b448.1560521297; _lxsdk_s=16b565146fc-949-60b-c81%7C%7C20',
        '_lxsdk_cuid=16b56528d4ac8-01b893a2eb2cd4-37c143e-144000-16b56528d4ac8; _lxsdk=16b56528d4ac8-01b893a2eb2cd4-37c143e-144000-16b56528d4ac8; _hc.v=040367fa-ec9b-4cd6-76b4-ddf5a8dbbd8a.1560521381; _lxsdk_s=16b56528bff-5b-747-873%7C%7C20',
        '_lxsdk_cuid=16b5654da2bc8-0878ac66b06951-37c143e-144000-16b5654da2bc8; _lxsdk=16b5654da2bc8-0878ac66b06951-37c143e-144000-16b5654da2bc8; _hc.v=a69716dd-28b5-e00a-f50c-5ecada6e14d2.1560521532; _lxsdk_s=16b565495d9-f08-b12-363%7C%7C17',
        ''
    ]
    cookie = random.choice(cookies)  # random.choice(),从列表中随机抽取一个对象
    return cookie
