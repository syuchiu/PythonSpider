"""
@file:proxy.py
@time:2019/6/10-22:36
"""
import requests

# 代理服务器
proxyHost = "http-dyn.abuyun.com"
proxyPort = "9020"

# 代理隧道验证信息
proxyUser = ""
proxyPass = ""

proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    "host": proxyHost,
    "port": proxyPort,
    "user": proxyUser,
    "pass": proxyPass,
}

proxies = {
    "http": proxyMeta,
    "https": proxyMeta,
}

# 要访问的目标页面
targetUrl = "http://test.abuyun.com"
# 待测试目标网页
# targetUrl = "http://icanhazip.com"

# resp = requests.get(targetUrl, proxies=proxies)
#
# print(resp.text)
