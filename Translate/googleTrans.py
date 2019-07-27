"""
@file:google.py
@time:2019/7/21-20:49
"""
import re
import urllib.parse
import requests
from googleDecrypt import get_tk
from fake_useragent import UserAgent


# client: webapp

# sl: auto --source language
# tl: en --to language

# hl: zh-CN

# dt: at
# dt: bd
# dt: ex
# dt: ld
# dt: md
# dt: qca
# dt: rw
# dt: rm
# dt: ss
# dt: t
# dt: gt

# source: bh
# ssel: 0
# tsel: 0
# kc: 1

# tk: 255557.345789  # 根据tkk和q
# q: 你好
# https://translate.google.cn/translate_a/single?client=webapp&sl=en&tl=zh-CN&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&otf=1&ssel=0&tsel=0&kc=1&tk=725262.897100&q=%E4%BD%A0%E5%A5%BD
# https://translate.google.cn
class GoogleTrans:
    def __init__(self, words, targetLang='en'):
        self.api = "https://translate.google.cn/translate_a/single?"
        self.url = "https://translate.google.cn"
        self.ua = UserAgent()
        self.session = requests.Session()
        self.words = words
        self.targetLang = targetLang

    def get_headers(self):
        headers = {
            'Host': 'translate.google.cn',
            'method': 'GET',
            'scheme': 'https',
            'accept': '*/*',
            'referer': "https://translate.google.cn/",
            'Connection': 'keep-alive',
            'user-agent': self.ua.random,
        }
        return headers

    def get_tkk(self):
        resp = self.session.get(self.url, headers=self.get_headers())
        PATTERN_TKK = re.compile(r"tkk:'(.*?)',", re.S)
        tkk = re.findall(PATTERN_TKK, resp.text)[0]

        return tkk

    def get_params(self, words):
        """
        请求需要的参数
        :return:
        """
        tkk = self.get_tkk()
        tk = get_tk(tkk, words)

        if self.targetLang == 'en':
            key = ['client', 'sl', 'tl', 'hl', 'dt',
                   'dt', 'dt', 'dt', 'dt', 'dt', 'dt',
                   'dt', 'dt', 'dt', 'dt', 'source',
                   'ssel', 'tsel', 'kc', 'tk', 'q']

            val = ['webapp', 'zh-CN', 'en', 'zh-CN', 'at',
                   'bd', 'ex', 'ld', 'md', 'qca',
                   'rw', 'rm', 'ss', 't', 'gt', 'bh',
                   '0', '0', '1', tk, self.words]

        elif self.targetLang == 'zh-CN':
            key = ['client', 'sl', 'tl', 'hl', 'dt',
                   'dt', 'dt', 'dt', 'dt', 'dt', 'dt',
                   'dt', 'dt', 'dt', 'dt', 'source',
                   'ssel', 'tsel', 'kc', 'tk', 'q']

            val = ['webapp', 'en', 'zh-CN', 'zh-CN', 'at',
                   'bd', 'ex', 'ld', 'md', 'qca',
                   'rw', 'rm', 'ss', 't', 'gt', 'bh',
                   '0', '0', '1', tk, self.words]

        else:
            print('Not support target language:%s yet' % self.targetLang)

        result = ''

        for i in range(len(key) - 1):
            result += key[i] + '=' + val[i] + '&'

        result += key[len(key) - 1] + '=' + urllib.parse.quote(words)

        return self.api + result

    def run(self):
        translate_api = self.get_params(self.words)
        resp = self.session.get(translate_api, headers=self.get_headers())
        result = resp.json()
        print("谷歌翻译:", result[0][0][0])


if __name__ == '__main__':
    words = input("输入单词：")
    targetLang = input("翻译语言：")
    g = GoogleTrans(words, targetLang)
    g.run()
