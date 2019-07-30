"""
@file:Qimingpian.py
@time:2019/7/28-13:18
"""
import os
import pickle
import pymongo
import execjs
import base64
import json
import requests

from Qilogin import QiSelenium


class QiMingPian:
    def __init__(self):
        self.product_api = "https://vipapi.qimingpian.com/DataList/productListVip"
        self.session = requests.session()
        self.data = {
            "time_interval": "",
            "tag": "",
            "tag_type": "and",
            "province": "",
            "lunci": "",
            "page": 1,
            "num": 20,
            "unionid": ""
        }
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.qimingpian.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
        }
        self.telephone = "xxxx"  # 输入自己的电话号码

    def login(self):
        """
        模拟登录企名片
        存在cookie文件则读取，否则再次模拟登录
        :return:
        """
        # data = {
        #     "mobile": 17826807096,
        #     "unionid": ""
        # }
        index_url = "https://www.qimingpian.com/finosda/project/pinvestment"
        if os.path.exists("cookies.pkl"):
            file_cookies = pickle.load(open("cookies.pkl", "rb"))
            # for cookie in cookies:
            #     self.session.cookies.set(cookie['name'], cookie['value'])
            # 测试cookies是否失效
            mycookies = QiSelenium(index_url, self.telephone, cookies=file_cookies)
            if mycookies is not None:
                print("采用保存的cookie登录:", mycookies)
            else:
                # 重新登录
                mycookies = QiSelenium(index_url, self.telephone)
        else:
            mycookies = QiSelenium(index_url, self.telephone)

        if mycookies is not None:
            for cookie in mycookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
                if cookie['name'] == 'gw_unionid':
                    print("unionid:", cookie['value'])
                    self.data['unionid'] = cookie['value']

    def get_product_data(self):
        page = 1
        while True:
            resp = self.session.post(self.product_api, headers=self.headers, data=self.data)
            product_dict = resp.json()
            if product_dict['status'] == 0:
                page = page + 1
                self.data['page'] = page
                encrypt_data = product_dict.get("encrypt_data")
                self.decrypt_data(encrypt_data)
            else:
                print(resp.text)
                print("可查看数据已完毕")
                break

    def decrypt_data(self, encrypt_data):
        with open('Qimingpian.js') as f:
            js_encrypt = f.read()

        ctx_encrypt = execjs.compile(js_encrypt)
        # 防止JS返回字符串内有特殊编码的字符将它转成base64再return，Python在解码
        decrypt_data = base64.b64decode(ctx_encrypt.call('o', encrypt_data))
        json_data = json.loads(decrypt_data)
        for i, value in enumerate(json_data['list']):
            print(i, value['product'], value['hangye1'], value['yewu'], value['money'])

    def save_to_mongo(self):
        pass

    def run(self):
        self.login()
        self.get_product_data()


if __name__ == '__main__':
    q = QiMingPian()
    q.run()
