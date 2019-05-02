import urllib
from io import BytesIO

import requests
import time
import re
import base64
import hmac
import hashlib
import json
import execjs
from matplotlib import pyplot as plt
from http import cookiejar
from PIL import Image
from urllib.parse import urlencode

# from profile import USERNAME, PASSWORD
from zhihu.debug.captcha.make import get_image_addr

HEADERS = {
    'connection': 'keep-alive',
    'host': 'www.zhihu.com',
    'referer': 'https://www.zhihu.com/',
    'user-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
}

LOGIN_URL = 'https://www.zhihu.com/signup'
LOGIN_API = 'https://www.zhihu.com/api/v3/oauth/sign_in'

# // "client_id=c3cef7c66a1843f8b3a9e6a1e3160e20&grant_type=password&timestamp=1555220173426&source=com.zhihu.web&signature=6805165c2470acc7fa170dab89c57f7aaded5b5d&username=%2B8617826807096&password=111111&captcha=&lang=cn&ref_source=other_%2Fhot&utm_source="
# 要加密的参数
FORM_DATA = {
    'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
    'grant_type': 'password',
    'source': 'com.zhihu.web',
    'signature': '',
    'username': '',
    'password': '',
    'captcha': '',
    'lang': 'cn',  # 改为'cn'是倒立汉字验证码
}


class ZhihuAccount(object):

    def __init__(self):
        self.login_url = LOGIN_URL
        self.login_api = LOGIN_API

        self.login_data = FORM_DATA.copy()

        self.session = requests.session()

        self.session.headers = HEADERS.copy()

        self.session.cookies = cookiejar.LWPCookieJar(filename='cookies.txt')

    def login(self, username=None, password=None, load_cookies=True):
        """
        模拟登录知乎
        :param username: 登录手机号
        :param password: 登录密码
        :param load_cookies: 是否读取上次保存的 Cookies
        :return: bool
        """
        # 如果存在cookie文件则直接加载
        if load_cookies and self.load_cookies():
            if self.check_login():
                return True

        headers = self.session.headers.copy()

        headers.update({
            'content-type': 'application/x-www-form-urlencoded',
            'x-zse-83': '3_1.1',
            'x-xsrftoken': self._get_token()
        })

        username, password = self._check_user_pass(username, password)

        self.login_data.update({
            'username': username,
            'password': password
        })

        timestamp = str(int(time.time() * 1000))

        self.login_data.update({
            'captcha': self._get_captcha(self.session.headers),

            'timestamp': timestamp,
            'signature': self._get_signature(timestamp),

            'ref_source': 'homepage',
            'utm_source': ''
        })

        # Read js file and compile, then call the encrypt function
        js_code = open('encrypt.js', 'r', errors='ignore', encoding='utf-8').read()
        encryption = execjs.compile(source=js_code)

        encrypted_data = encryption.call('Q', urlencode(self.login_data))
        print("data:",urlencode(self.login_data))
        # print("encrypted_data：%s" % encrypted_data)
        resp = self.session.post(self.login_api, data=encrypted_data, headers=headers)
        print("login resp:", resp.text, resp.status_code)
        # 1111&captcha=%7B%22img_size%22%3A%5B200%2C44%5D%2C%22input_points%2 编码了两次
        if 'error' in resp.text:
            print(re.findall(r'"message":"(.*?)"', resp.text)[0])

        elif self.check_login():
            return True

        print('Login failed')

        return False

    def load_cookies(self):
        """
        读取 Cookies 文件加载到 Session
        :return: bool
        """
        try:
            self.session.cookies.load(ignore_discard=True)
            return True
        except IOError:
            return False

    def check_login(self):
        """
        检查登录状态，访问登录页面出现跳转则是已登录，
        如登录成功保存当前 Cookies
        :return: bool
        """
        resp = self.session.get(self.login_url, allow_redirects=True)

        if resp.history[0].status_code == 302:
            self.session.cookies.save()

            resp = self.session.get(self.login_url)
            with open("zhihu.html", 'w', encoding='utf8') as f:
                f.write(resp.text)

            print('Login succeeded')
            return True

        return False

    def _get_token(self):
        """
        从登录页面获取 token
        :return:
        """
        resp = self.session.get(self.login_url)

        token = re.findall(r'_xsrf=([\w|-]+)', resp.headers.get('Set-Cookie'))[0]

        return token

    def _get_captcha(self, headers):
        """
        请求验证码的 API 接口，无论是否需要验证码都需要请求一次
        如果需要验证码会返回图片的 base64 编码
        根据头部 lang 字段匹配验证码，需要人工输入
        :param headers: 带授权信息的请求头部
        :return: 验证码的 POST 参数
        """
        lang = self.login_data.get('lang', 'en')

        if lang == 'cn':
            api = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=cn'
        else:
            api = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=en'

        resp = self.session.get(api, headers=headers)

        show_captcha = re.search(r'true', resp.text)

        if show_captcha:

            put_resp = self.session.put(api, headers=headers)

            img_base64 = re.findall(
                r'"img_base64":"(.+)"', put_resp.text, re.S)[0].replace(r'\n', '')

            # with open('./captcha.jpg', 'wb') as f:
            #     f.write(base64.b64decode(img_base64))
            # img = Image.open('./captcha.jpg')

            img = Image.open(BytesIO(base64.b64decode(img_base64)))

            img.show()

            captcha = input("请输入图片验证码 如果为倒立图片请输入第几个文字以,为间隔(输入数字)")
            img.close()

            if lang == 'cn':
                captcha = get_image_addr(captcha)
                capt = json.dumps(captcha).replace(" ", "")
            # plt.imshow(img)
            # print('点击所有倒立的汉字，按回车提交')
            # points = plt.ginput(7)
            # capt = json.dumps({'img_size': [200, 44],
            #                    'input_points': [[i[0] / 2, i[1] / 2] for i in points]})
            else:
                img.show()
                capt = input('请输入图片里的验证码：')

            print("capt:", capt)
            # 这里必须先把参数 POST 验证码接口
            resp = self.session.post(api, data={'input_text': capt}, headers=headers)
            print("resp:", resp.text)
            return capt
        return ''

    def _get_signature(self, timestamp):
        """
        通过 Hmac 算法计算返回签名
        实际是几个固定字符串加时间戳
        :param timestamp
        :return: signature
        """
        ha = hmac.new(b'd1b964811afb40118a12068ff74a12f4', digestmod=hashlib.sha1)
        grant_type = self.login_data['grant_type']
        client_id = self.login_data['client_id']
        source = self.login_data['source']
        ha.update(bytes((grant_type + client_id + source + timestamp), encoding='utf-8'))
        return ha.hexdigest()

    def _check_user_pass(self, username, password):
        """
        检查用户名和密码是否已输入，若无则手动输入
        """
        if username is None:
            username = self.login_data.get('username')
            if not username:
                username = input('请输入手机号：')
        if '+86' not in username:
            username = '+86' + username

        if password is None:
            password = self.login_data.get('password')
            if not password:
                password = input('请输入密码：')
        return username, password


if __name__ == '__main__':
    USERNAME = "+86" # 账号
    PASSWORD = "" # 密码
    account = ZhihuAccount()
    account.login(username=USERNAME, password=PASSWORD, load_cookies=True)
