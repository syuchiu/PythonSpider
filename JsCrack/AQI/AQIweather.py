"""
@file:AQIweather.py
@time:2019/7/30-14:17
"""
# JScript
# JavaScriptCore
# Nashorn
# Node
# PhantomJS
# PyV8
# SlimerJS
# SpiderMonkey
import json
from pprint import pprint
import pymongo
import requests
import execjs


def execute_js(url, method, city):
    # Compile javascript
    file = 'AQIweather.js'
    text = open(file, encoding='utf8').read()
    ctx = execjs.compile(text)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"

    }
    # GET PARAM
    js = 'getParam("{0}", "{1}")'.format(method, city)
    params = ctx.eval(js)
    data = {'d': params}
    response = requests.post(url, data=data, headers=headers)
    # Decode data
    js = 'decodeData("{0}")'.format(response.text)
    decrypted_data = json.loads(ctx.eval(js))

    return decrypted_data


if __name__ == '__main__':
    # init
    if execjs.get().name != "Node.js (V8)":
        raise Exception('Node Environment error')
    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    db = myclient['weather']
    coll = db['AQI']
    # Param
    url = "https://www.aqistudy.cn/apinew/aqistudyapi.php"
    method = "GETDATA"
    city = "宁波"

    decrypted_data = execute_js(url, method, city)
    pprint(decrypted_data)
    rows = decrypted_data['result']['data']['rows']
    for row in rows:
        item = {}
        item['cityname'] = row.get('cityname')
        item['pointname'] = row.get('pointname')
        item['quality'] = row.get('quality')
        item['pm2_5'] = row.get('pm2_5')
        coll.insert_one(item)
