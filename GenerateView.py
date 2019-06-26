"""
@file:GenerateView.py
@time:2019/6/24-23:16
"""
import logging
import re
import time
from selenium import webdriver
from requests_html import HTMLSession
from fake_useragent import UserAgent
from urllib.parse import urljoin

ua = UserAgent()  # 调用UserAgent类生成ua实例

# 1.生成session
session = HTMLSession()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
mybrowser = webdriver.Chrome(chrome_options=chrome_options)


# 请求列表页提取详情页链接 浏览量未增加
def get_html(url):
    headers = {
        'user-agent': ua.random,  # ua实例调用random方法随机返回一个ua字符串
    }

    view_headers = {
        'user-agent': ua.random,
        "origin": "https://www.jianshu.com"
    }
    if not isinstance(url, list):
        response = session.get(url=url, headers=headers)
        temp_links = response.html.xpath("//a[@class='title']/@href")
        details_links = [urljoin(url, temp) for temp in temp_links]

        return details_links
    else:
        for link in url:
            # https://www.jianshu.com/notes/01b80c4b78ec/mark_viewed.json
            Viewjson = "https://www.jianshu.com/notes/{}/mark_viewed.json"
            uuid_pattern = r"\"uuid\":\"(.*?)\""
            resp = session.get(url=link, headers=headers)
            articleID = link[link.rindex('/') + 1:]
            print("ID:", articleID, "+1")
            # 正则提取uuid
            data = dict()
            uuid = re.findall(uuid_pattern, resp.html.html)[0]
            data['uuid'] = uuid
            view_headers['referer'] = link
            ViewUrl = Viewjson.format(articleID)
            session.post(url=ViewUrl, headers=view_headers, data=data)
            time.sleep(1)


if __name__ == '__main__':
    url = "https://www.jianshu.com/u/8524376e970d"
    links = get_html(url)
    for _ in range(1000):
        print("links start")
        get_html(links)
        logging.info("浏览次数:%s", _)
        time.sleep(2)
        # for link in links:
        #     mybrowser.get(link)
        #     time.sleep(1)
