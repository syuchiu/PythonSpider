import codecs
import random
import re
import time
import requests
from pymongo import MongoClient

from scrapy import Selector
from bs4 import BeautifulSoup as bs, Tag
from fake_useragent import UserAgent
from selenium import webdriver

from constants import *
from decrypt import _decrypt_text_tag, _decrypt_textPath_tag, _decrypt_woff_tag
from logtofile import init_logger, get_cookie

# 调用UserAgent类生成ua实例
from proxy import proxies
from word import dictionary

ua = UserAgent(verify_ssl=False)


class DpFont:
    def __init__(self, name):
        print("init ok")
        self.DpLogger = init_logger(log_name=name)
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['dianping']
        self.collection = self.db['shop']

        self.session = requests.session()
        # 请求代理链接必须2s后
        # time.sleep(2)
        # self.proxies = {"http": self.get_proxy().strip()}
        # self.browser = webdriver.Chrome()

    def get_proxy(self):
        """
        获取芝麻代理
        :return: ip:port
        """
        proxyMeta = requests.get(PROXY_URL).text
        return proxyMeta

    def parse_url(self, url, headers=None):
        """
        解析页面
        :param url: 请求链接
        :param headers: 请求头
        :return: response
        """
        if headers:
            headers['user-agent'] = ua.random
        else:
            # 请求CSS文件时不可携带session里的cookie
            resp = requests.get(url, headers=CSS_HEADERS)
            return resp

        # headers['Cookie'] = get_cookie()
        # todo 需要将阿布云代理换成自己的才可使用
        self.proxies = proxies
        response = self.session.get(url, headers=headers, proxies=self.proxies)
        # try:
        #     response = self.session.get(url, headers=headers, proxies=self.proxies)
        # except Exception as e:
        #     print("代理失效")
        #     self.proxies = {"http": self.get_proxy().strip()}
        #     response = self.session.get(url, headers=headers, proxies=self.proxies)

        if response.history and response.history[0].status_code == 302:
            # 将重定向链接写入日志
            print("出现重定向")
            self.DpLogger.warning("验证码：%s", response.url)
            return None

        return response

    def get_css(self, html):
        """
        提取svgcss链接
        :param html: 列表页html
        :return: CSS文件内容
        """
        # re.M多行模式
        # In [6]: re.findall(r"\w+$",s,re.M)
        # Out[6]: ['boy', 'girl'] 若去掉则只匹配girl
        svg_text_css = re.search(PATTERN_SVG_CSS, html, re.M)

        if not svg_text_css:
            print("html:", html)
            raise Exception("cannot find svgtextcss file")

        css_url = svg_text_css.group(1)
        content = self.parse_url(CSS_URL_PREFIX + css_url)

        return content

    @staticmethod
    def parse_shop_css(css):
        """
        解析CSS文件
        :param self:
        :param css: CSS文件内容
        :return:(sjipiv,x,y)
        """
        # 偏移量字典存储
        css_px_dict = {}
        # svg的url dict储存
        svg_url_dict = {}

        # r'.(.*?){background:(.*?)px(.*?)px;}' (sjipiv,x,y)
        css_px = re.findall(PATTERN_BACKGROUND, css)
        if not css_px:
            raise Exception("cannot find css px")

        # r'\[class\^="(.+?)"\]{width:(.+?)px;.+?url\((.+?)\)' ('dmc','12','svg')
        svg_urls = re.findall(PATTERN_SPAN_CLASS, css)
        if not svg_urls:
            raise Exception("cannot find svg file")

        for i in svg_urls:
            svg_url_dict.update({i[0]: [int(i[1].strip()), PAGE_PREFIX + i[2]]})

        for i in css_px:
            css_px_dict[i[0]] = {
                'x': -int(i[1].strip()),
                'y': -int(i[-1].strip()),
            }

        return css_px_dict, svg_url_dict

    def decrypt(self, address_tag_soup, svg_url_dict, css_px_dict):
        """
        获取标签里包含的子节点，判断子节点是否为纯文本若不是判断应用何种方式，采取相应方式解决
        :param address_tag_soup:
        :param svg_url_dict:
        :param css_px_dict:
        :return:
        """
        # 获取该节点下的所有直接子节点
        contents = address_tag_soup.contents

        text = ""
        while contents:
            methods = 0
            node = contents.pop(0)
            # print("the node:", node)
            # 判断该标签是否为标签，若为文字则直接追加
            if isinstance(node, Tag):
                # 标签名为列表中的几项视为加密标签，否则直接提取文本
                if node.name in DECRYPT_TAGS and node['class'][0] not in IGNORED_SPAN_CLASS:
                    # 判断标签的类及对应的方式若为自定义字体
                    for svg_name in svg_url_dict.keys():

                        if node['class'][0].startswith(svg_name):
                            methods = 1
                            break

                    node = self.get_decrypted(node, svg_url_dict, css_px_dict, methods)
                else:
                    text += node.string

            elif not isinstance(node, str):
                continue

            text += node

        return text.strip()

    def get_decrypted(self, node, svg_url_dict, css_px_dict, methods):
        """
        :param node: 要解析的节点
        :param svg_url_dict: 略
        :param css_px_dict: 略
        :param methods:1 自定义字体 0 svg格式
        :return:
        """
        if not methods:
            unitext = node.get_text().encode('raw_unicode_escape').replace(b'\u', b'').decode()
            text = _decrypt_woff_tag(unitext, dictionary)
            # print("font:", text)
        else:
            font_size, svg_url = None, None

            # 1、根据CSS的名称获取偏移量
            css_class = node['class'][0]

            x_offset, y_offset = css_px_dict[css_class]['x'], css_px_dict[css_class]['y']

            # 2、获取字宽请求svg链接，判断textPath是否存在确定种类
            for svg_name in svg_url_dict.keys():
                if css_class.startswith(svg_name):
                    font_size = svg_url_dict[svg_name][0]
                    svg_url = svg_url_dict[svg_name][1]
                    break

            svg_content = self.parse_url(svg_url).text
            # 3、解析获取真实的文字
            if "textPath" in svg_content:
                print("开始textPath解析")
                text = _decrypt_textPath_tag(svg_content, font_size, x_offset, y_offset)
            else:
                text = _decrypt_text_tag(svg_content, font_size, x_offset, y_offset)

        return text

    def __call__(self):
        # 1、请求列表页
        content = self.parse_url(START_URL, HEADERS)
        if content is None:
            return None

        with codecs.open('txt/shoplist.html', 'w', encoding='utf-8') as f:
            f.write(content.text)

        # 2、提取详情页链接并请求
        resp = Selector(content)
        shops = resp.xpath("//div[@id='shop-all-list']/ul//div[@class='tit']/a[1]/@href").extract()
        print("shops:", shops)
        for shop_url in shops:
            print("start parse shop:", shop_url)
            item = {}

            while True:
                try:
                    shop_content_text = self.parse_url(shop_url, SHOP_HEADERS).text
                    break
                except Exception as e:
                    print("shop_content in error:", e)
                    time.sleep(20)

            # 3、获取CSS文件
            while True:
                try:
                    content_css = self.get_css(shop_content_text).text
                    break
                except Exception as error:
                    print("获取CSS文件出错，可能文件不完整")
                    time.sleep(10)
                    shop_content_text = self.parse_url(shop_url, SHOP_HEADERS).text

            # 4、获取当前详情页class对应坐标,class对应svg链接
            css_px_dict, svg_url_dict = self.parse_shop_css(content_css)

            # 5、获取需要解密的标签 span id addresss
            shop_page_soup = bs(shop_content_text, 'lxml')

            address_tag = shop_page_soup.find(id='address')
            # 6、解密标签返回正确文本
            shop_name = shop_page_soup.find(name='h1', class_="shop-name").text
            text = self.decrypt(address_tag, svg_url_dict, css_px_dict)
            print(f'\n>> 解密后内容：\n {text}')
            item['name'] = shop_name
            item['address'] = text
            # 7、存储到mongodb
            self.collection.insert_one(item)
            time.sleep(random.uniform(*COMMENTS_SLEEP))


if __name__ == '__main__':
    name = "dianping"
    dianping = DpFont(name)
    dianping()
