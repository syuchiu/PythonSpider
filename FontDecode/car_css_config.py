"""
@file:car_config.py
@time:2019/6/16-10:38
"""
import json
import re
import execjs
import requests
from scrapy import Selector

# 正则表达式
config_pattern = r'var config = (.*?);'
# 应对&nbsp;
option_pattern = r'var option = (.*?});'
baike_pattern = r'var keyLink = (.*?);'
# 车型
specIDs_pattern = r'var specIDs =(.*?);'
optionjs, configjs = "", ""

# 原Js中的代码替换增加一条插入语句
tempJs = "var $tempArray$ = $GetElementsByCss$($GetClassName$($index$));"

insertJs = "dic[$GetClassName$($index$)]  = $item$;var $tempArray$ = $GetElementsByCss$($GetClassName$($index$));"

# specIDs = [39464, 39465, 39466, 39467, 39468, 39469, 37411, 37412, 37413, 37414, 37415, 37416]
# functionjs = r"var \$tempArray\$ = \$GetElementsByCss\$\(\$GetClassName\$\(\$index\$\)\);"


# 不知道execjs如何处理自调用JS函数,进行修改成普通函数，通过test进行调用
prefix = """var jsdom = require("jsdom");
var {JSDOM} = jsdom;
var dom = new JSDOM();
var dic = {}

window = dom.window;
document = window.document;
window.decodeURIComponent = decodeURIComponent;
"""
postfix = """
function test() {
    ftx(document);
    return dic;
}
"""
output = """
dic[$GetClassName$($index$)]  = $item$;
"""


def get_html():
    url = "https://car.autohome.com.cn/config/series/4658.html#pvareaid=3454437"
    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36"
    }
    with requests.get(url=url, headers=headers, timeout=3) as res:
        root = Selector(res)
        html = res.content.decode("utf-8")

    return html, root


# 这段代码很烂暂时没改进思路
def get_name(info_dict, id, car_name_dict=None):
    data = {}
    infos = info_dict['result']['configtypeitems']

    for info in infos:
        for item in info['configitems']:

            if item['id'] == id:
                data['name'] = item['name']

                if car_name_dict is not None:
                    for specid, dname in car_name_dict.items():
                        # {'price': [], 'specid': 39464, 'sublist': [], 'value': '主●&nbsp;/&nbsp;副●'}
                        for value_dict in item['valueitems']:
                            if specid == value_dict["specid"]:
                                data[dname] = value_dict["value"]
                return data


def js_exec(jsfile, car_info):
    ctx = execjs.compile(jsfile)
    tt = ctx.call('test')
    # car_info 先前提取出来含有span的字符串
    # span_list = re.findall("<span(.*?)></span>", car_info)

    for k, v in tt.items():
        k = k.replace('.', '').strip()
        # 全文替换
        car_info = car_info.replace(str("<span class='" + k + "'></span>"), v)

    info_dict = json.loads(car_info)
    return info_dict


if __name__ == '__main__':
    html, root = get_html()
    # 提取自调用的函数
    js_list = re.findall(r'(function\([a-zA-Z]{2}.*?_\).*?)\)\(document\);', html)
    specIDs = eval(re.findall(specIDs_pattern, html)[0])
    # print(specIDs, type(specIDs))
    car_option = re.findall(option_pattern, html, re.S)[0]
    car_config = re.findall(config_pattern, html, re.S)[0]
    # 会匹配到三段js分别对应baike，config，option，以option作为示范例子
    for js in js_list:
        if "_config" in js:
            configjs = js
        elif "_option" in js:
            optionjs = js

    # 拼接成可用execjs调用的形式
    optionJs = prefix + '\n' + optionjs.replace(tempJs, insertJs).replace('function', 'function ftx',
                                                                          1) + '\n' + postfix
    configJs = prefix + '\n' + configjs.replace(tempJs, insertJs).replace('function', 'function ftx',
                                                                          1) + '\n' + postfix

    option_dict = js_exec(optionJs, car_option)
    config_dict = js_exec(configJs, car_config)
    # 获取车型名称的字典{'specid': 39464, 'value': '宝马X3 2019款 xDrive25i 豪华套装'},
    paramitems_list = config_dict['result']['paramtypeitems'][0]['paramitems'][0]['valueitems']
    # 构造id对应车名的字典
    car_name_dict = dict([(param['specid'], param['value']) for param in paramitems_list])

    # 每款车的安全气囊
    print(get_name(option_dict, 28, car_name_dict))
    # 膝部气囊
    print(get_name(option_dict, 23, car_name_dict))
