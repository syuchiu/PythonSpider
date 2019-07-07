"""
@file:script.py
@time:2019/6/29-22:35
"""
from mitmproxy import http
from mitmproxy import ctx


# 方法名和参数的名称是固定的
def request(flow: http.HTTPFlow) -> None:
    # 打印当前截获到的请求头
    # print(flow.request.headers)
    # 日志形式输出请求链接
    ctx.log.warn(flow.request.url)
    # 修改请求链接
    url = "http://httpbin.org/get"
    flow.request.url = url
    # 将请求新增了一个查询参数
    flow.request.query["mitmproxy"] = "test"
    # 将请求头的UA改成MitmProxy
    flow.request.headers['User-Agent'] = "MitmProxy"


def response(flow: http.HTTPFlow) -> None:
    # 将响应头中新增了一个自定义头字段
    flow.response.headers["newheader"] = "test"
    # print("cookies:", flow.response.cookies)
    # 日志输出响应文本
    ctx.log.info(str(flow.response.text))
