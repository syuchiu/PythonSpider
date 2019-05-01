"""
@author:hp
@project:10-zhihu
@file:make.py
@ide:PyCharm
@time:2019/4/30-16:58
"""
from zhihu.debug.captcha.constants import input_points


def get_cookie(cookie):
    new_cookie = {}

    for line in cookie.split(';'):
        try:
            key, value = line.split('=', 1)

            new_cookie[key] = value

        except Exception as e:
            print(e)

    return new_cookie


def set_cookie(cookie, new_cookie):
    for k, v in new_cookie.items():

        cookie[k] = v

    return cookie


def get_image_addr(img_str):
    if "，" in img_str:
        img_str = img_str.replace("，", ",")

    img_list = img_str.split(",")
    captcha = {"img_size": [200, 44], "input_points": []}

    for i in img_list:
        captcha['input_points'].append(input_points[int(i) - 1])

    return captcha
