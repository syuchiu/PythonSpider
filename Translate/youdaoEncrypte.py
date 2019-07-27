"""
@file:encryption.py
@time:2019/7/16-15:13
"""
import hashlib
import random
import time


def get_md5(text):
    """
    在python3中使用hashlib模块进行md5操作
    :param text:
    :return:
    """
    # 创建md5对象
    hl = hashlib.md5()
    hl.update(text.encode(encoding='utf-8'))

    # print('MD5加密后为 ：' + hl.hexdigest())
    return hl.hexdigest()


def get_ts_salt():
    """
    :return:
    """
    # ts是r = "" + (new Date).getTime()是时间戳返回距 1970 年 1 月 1 日之间的毫秒数
    ts = str(int(time.time() * 1000))
    # parseInt(10 * Math.random(), 10) 以十进制解析字符串返回整数
    salt = ts + str(random.randint(0, 10))
    return ts, salt


def get_sign(key, salt):
    """
    sign: n.md5("fanyideskweb" + e + i + "97_3(jkMYg@T[KZQmqjTK")
    :return:
    """
    sign = "fanyideskweb" + key + salt + "97_3(jkMYg@T[KZQmqjTK"
    return get_md5(sign)
