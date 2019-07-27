"""
@file:baidu.py
@time:2019/7/16-16:32
"""
import json

import requests
import re
import execjs

"""
请求的参数信息

from：翻译的语言类型
to： 翻译成哪种语言
query：翻译的内容
transtype：translang
simple_means_flag：3 固定值
sign：
token：页面源码中可提取
"""

# 正则匹配规则
PATTERN_GTK = r"window.gtk = '(.*?)';"
PATTERN_TOKEN = r"window\['common'\].*?token: '(.*?)'"


# 日语 jp
# 中文 zh
# 英文 en

class BaiduTranslate:
    def __init__(self, key, to=None):
        self.key = key
        self.to = to
        self.url = "https://fanyi.baidu.com/"
        self.session = requests.session()
        self.gtk, self.token = self.get_gtk_token()
        self.gtk, self.token = self.get_gtk_token()

    def generateSign(self):
        """
        生成sign
        :return:
        """
        # modify_js = "var i = {};".format(self.gtk)
        with open("baiduTrans.js", "r", encoding="utf8") as f:
            trans_in_file = f.read()
        try:
            transText = trans_in_file.replace("function e(r) {", "function e(r,i) {")
        except:
            raise Exception("transText error")
        ctx = execjs.compile(transText)
        sign = ctx.call('e', self.key, self.gtk)

        return sign

    def get_gtk_token(self):
        """
        得到页面源码中的token和gtk
        :return:
        """
        resp = self.session.get(self.url, headers=self.get_headers())
        # 提取gtk/token
        gtk = re.findall(PATTERN_GTK, resp.text, re.S)[0]
        token = re.findall(PATTERN_TOKEN, resp.text, re.S)[0]
        return gtk, token

    def langdetect(self):
        """
        判断输入文字类型{"error":0,"msg":"success","lan":"en"}
        :param query:
        :return:
        """
        langdetect_url = "https://fanyi.baidu.com/langdetect"
        data = {'query': self.key}
        response = requests.post(langdetect_url, data=data, headers=self.get_headers())
        str_type = json.loads(response.content.decode())['lan']

        if not self.to:
            to_type = "en" if str_type == 'zh' else "en"
        else:
            to_type = self.to

        return str_type, to_type

    def v2transapi(self, str_type, to_type):
        v2transapi_url = "https://fanyi.baidu.com/v2transapi"
        sign = self.generateSign()
        data = {
            'from': str_type,
            'to': to_type,
            'query': self.key,
            'simple_means_flag': 3,
            'transtype': 'translang',
            'sign': sign,
            'token': self.token
        }
        response = self.session.post(v2transapi_url, headers=self.get_headers(), data=data)
        try:
            trans_result = json.loads(response.content.decode())['trans_result']['data'][0]['dst']
            return trans_result
        except Exception as e:
            print(response.text)

    def get_headers(self):
        UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
        headers = {
            "User-Agent": UA,
            'Host': 'fanyi.baidu.com',
            'Origin': 'https://fanyi.baidu.com',
        }
        return headers

    def run(self):
        str_type, to_type = self.langdetect()
        trans_result = self.v2transapi(str_type, to_type)
        print('百度翻译:{}'.format(trans_result))


if __name__ == '__main__':
    keys = input("需要翻译的文字:")
    to = input("翻译语言：")

    b = BaiduTranslate(keys, to)
    b.run()
