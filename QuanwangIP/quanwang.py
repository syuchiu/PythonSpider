"""
@file:quanwang.py
@time:2019/7/4-23:47
"""
import re

import requests
from scrapy import Selector

# PATTERN_SUB = r"<div .*?inline-block;\"></div>|<p .*?none;\">.*?</p>|<span *?inline-block;\"></span>|<span></span>"
PATTERN_div = r"<div style=\"display:inline-block;\"></div>|<div style=\"display: inline-block;\"></div>"
PATTERN_p = r"<div style=\"display:none;\">.*?</div>|<div style=\"display: none;\">.*?</div>"
PATTERN_span = r"<span></span>"
PATTERN_span1 = r"<p style=\"display:none;\">.*?</p>|<p style=\"display: none;\">.*?</p>"


def get_real_port(classValue):
    port_ = ""
    for value in classValue:
        port_ += str("ABCDEFGHIZ".index(value))
    port = int(port_) >> 3
    return str(port)


def get_html(url):
    resp = requests.get(url, headers=headers)
    # text = response.text
    response = Selector(resp)

    contentIP = response.xpath("//table[@class='table table-hover']//tr")

    for tdIP in contentIP[1:]:
        portClass = tdIP.xpath(".//td[@class='ip']/span[last()]/@class").extract_first()
        iptag = ''.join(tdIP.xpath(".//td[@class='ip']/*[not(contains(@class,'port'))]").extract())

        if portClass:
            # 得到Port的第二个class 47.102.216.176:3128
            classValue = portClass.split(' ')[1]
            port = get_real_port(classValue)

            # cleanTag = re.sub(PATTERN_SUB, "", iptag, re.S)
            cleanTag = re.sub(PATTERN_div, "", iptag, re.S)
            cleanTag = re.sub(PATTERN_p, "", cleanTag, re.S)
            cleanTag = re.sub(PATTERN_span, "", cleanTag, re.S)
            cleanTag = re.sub(PATTERN_span1, "", cleanTag, re.S)

            ip_resp = Selector(text=cleanTag)
            ip_addr = ''.join(ip_resp.xpath(".//text()").extract())
            ip_full = ip_addr + ":" + port
            print(ip_full)


if __name__ == '__main__':
    url = "http://www.goubanjia.com/"
    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"

    headers = {
        "User-Agent": UA
    }

    get_html(url)
