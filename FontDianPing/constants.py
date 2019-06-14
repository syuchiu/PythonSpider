"""
@file:constants.py
@time:2019/6/4-9:12
"""
# 芝麻代理测试
PROXY_URL = ""
# 阿布云代理

# 列表页请求头
HEADERS = {
    "Referer": "http://www.dianping.com/",
    "Upgrade-Insecure-Requests": '1',
    'Host': 'www.dianping.com',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
}

SHOP_HEADERS = {
    "Referer": "https://www.dianping.com/hangzhou/ch10/g101",
    "Upgrade-Insecure-Requests": '1',
    'Host': 'www.dianping.com',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
}
# CSS请求头
CSS_HEADERS = {
    'Host': 's3plus.meituan.net',
    'Upgrade-Insecure-Requests': '1',
}

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36"
# 随机延时
COMMENTS_SLEEP = (20, 30)

# CSS中提取类名坐标
PATTERN_BACKGROUND = r'.([a-zA-Z0-9-]+){background:(.*?).0px(.*?).0px;}'
# 提取SVG链接
PATTERN_SPAN_CLASS = r'\[class\^="(.+?)"\]{width:(.+?)px;.+?url\((.+?)\)'
# 从正文提取CSS
PATTERN_SVG_CSS = r'href="([^"]+svgtextcss[^"]+)"'
PATTERN_SVG_TEXT = r'y=.*?(\d+)">(.*?)</text>'

# 请求协议
PAGE_PREFIX = "https:"
# 请求资源前缀
CSS_URL_PREFIX = 'http:'
# 请求的列表页
START_URL = "https://www.dianping.com/hangzhou/ch10/g101"
# 加密的标签
DECRYPT_TAGS = ['d', 'e', 'svgmtsi', 'span']

# 加密文本中无效的标签
IGNORED_SPAN_CLASS = ['info-name', ]
# 允许网络请求的HTTP方法
HTTP_METHODS = ['get', 'head', 'post', 'put', 'options']

# 启用日志
LOG_ENABLE = True
# 日志级别
LOG_LEVEL = 'INFO'
# 日志文件编码
LOG_FILE_ENCODING = 'UTF-8'
# 日志文件路径
LOG_FILE_SAVE_PATH = r'txt/dianping.log'
# 日志时间格式
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
# 日志级别对应格式
LOG_FORMAT = {
    'DEBUG': '%(asctime)s %(name)s(%(levelname)s) - %(message)s',
    'INFO': '%(asctime)s %(name)s(%(levelname)s) - %(message)s',
    'WARNING': '%(asctime)s %(name)s(%(levelname)s) - %(message)s',
    'ERROR': '%(asctime)s %(name)s(%(levelname)s) - %(message)s',
    'CRITICAL': '%(asctime)s %(name)s(%(levelname)s) - %(message)s',
}

# Mongodb配置
# MONGO_CLIENT = 'mongodb://localhost:27017'

