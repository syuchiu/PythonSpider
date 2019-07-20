"""
@file:hongshu.py
@time:2019/7/19-8:37
"""
import os
import re
import threading
import codecs
import time
from urllib.parse import urlparse, parse_qsl, urlencode

import execjs

from queue import Queue
from functools import wraps

from fake_useragent import UserAgent
from scrapy import Selector

from myhttp import request

mutex = threading.Lock()
ua = UserAgent()

general_url = "https://g.hongshu.com/content/{0}/{1}.html"
class_name = "context_kw"
# 提取JS代码
PATTERN_JS = r"(var CryptoJS=CryptoJS.*?)</script>"
PATTERN_sub_location = r"if\(top\[.*?}"
sub_js_for = "return words"
# 修改JS
prefix = """var jsdom = require("jsdom");
var {JSDOM} = jsdom;
var dom = new JSDOM();

window = dom.window;
document = window.document;
window.decodeURIComponent = decodeURIComponent;
"""


def run_time(func):
    @wraps(func)
    def wrapper(*args, **kw):
        start = time.time()
        func(*args, **kw)
        end = time.time()
        print('running', end - start, 's')

    return wrapper


# https://g.hongshu.com/chapterlist/93416.do
class HongShu:
    def __init__(self, Baseurl, folderName):
        self.folder = folderName
        self.page_num = 1
        self.thread_num = 5
        self.queue_url = Queue()
        self.Base = Baseurl
        # 解析url，获取url里面的各种组成成分
        parsed_url = urlparse(Baseurl)
        self.prefixUrl = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
        # 获取url组成成分里面的 query 参数部分
        self.query = dict(parse_qsl(parsed_url.query))
        # print(query) {'bid': '93416', 'pagesize': '50', 'sortby': 'ASC', 'pagenum': '1'}

    def get_detail_url(self, detail_url):
        headers = {
            "user-agent": ua.random
        }
        resp = request("get", detail_url, headers, return_type="json")
        chapters = resp['list']

        for chapter in chapters:
            chapter_url = general_url.format(chapter['bid'], chapter['chapterid'])
            self.queue_url.put(chapter_url)  # 生成URL存入队列，等待其他线程提取

        print("size:", self.queue_url.qsize())
        # 翻页
        if self.page_num < resp['totalpage']:
            self.page_num += 1
            self.query['pagenum'] = self.page_num
            next_url = self.prefixUrl + '?' + urlencode(self.query)
            print(next_url)
            self.get_detail_url(next_url)

    def get_content(self):
        while not self.queue_url.empty():  # 保证url遍历结束后能退出线程
            print(self.queue_url.qsize())
            headers = {
                "user-agent": ua.random,
                "referer": self.prefixUrl
            }
            detail_url = self.queue_url.get()  # 从队列中获取URL
            req_html = request("get", detail_url, headers)
            try:
                CryptoJS = re.findall(PATTERN_JS, req_html, re.S)[0]
            except Exception as e:
                print("Exception:", detail_url)
                return

            element_dict = self.deal_the_js(CryptoJS)
            self.replace_text(element_dict, req_html)
            print("-----" * 50)

    def deal_the_js(self, Jstext):
        Jstext = re.sub(PATTERN_sub_location, "", Jstext, re.S)
        text = prefix + '\n' + 'function test(){' + Jstext + '\n' + sub_js_for + '}'
        ctx = execjs.compile(text)
        words = ctx.call('test')
        element_dict = dict()
        for k, word in enumerate(words):
            element_dict[class_name + str(k)] = word

        return element_dict

    def replace_text(self, element_dict, req_html):
        # <span class="context_kw1"></span>
        # 语法格式：re.sub(pattern, repl, string, count=0)，返回值是修改后的结果字符串
        # replace 不会改变原 string 的内容
        for k, v in element_dict.items():
            req_html = req_html.replace("<span class=\"{}\"></span>".format(k), v)

        myselector = Selector(text=req_html)
        title = myselector.xpath("//h1/text()").extract_first()
        content = '\r\n'.join(myselector.xpath("//div[@class='rdtext']//text()").extract()).strip()
        # print(content)
        self.save_to_txt(title, content)

    def save_to_txt(self, title, content):
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)

        with codecs.open("{}/{}.txt".format(self.folder, title), "w", encoding="utf8") as f:
            f.write(content)

    def run(self):
        self.get_detail_url(self.Base)

        threaLists = []
        for _ in range(self.thread_num):
            new_thread = threading.Thread(target=self.get_content)
            new_thread.start()
            threaLists.append(new_thread)

        for new_thread in threaLists:
            new_thread.join()

        print('Data crawling is finished.')


if __name__ == '__main__':
    # url = "https://g.hongshu.com/bookajax/chapterlist/bid/93416.do?bid=93416&pagesize=50&sortby=ASC&pagenum=1"
    # https://g.hongshu.com/bookajax/chapterlist/bid/91323.do?bid=91323&pagesize=50&sortby=ASC&pagenum=1
    url = input("输入网址：")
    folderName = "HSW"
    h = HongShu(url, folderName)
    h.run()
