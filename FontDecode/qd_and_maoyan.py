import io
import os

import requests
import re

import requests_html
from fontTools.ttLib import TTFont

## 起点中文网 ##
# 1、定义英文单词的数字和数字之间的关系
convert_dict = {
    'one': '1',
    'two': '2',
    'three': '3',
    'four': '4',
    'five': '5',
    'six': '6',
    'seven': '7',
    'eight': '8',
    'nine': '9',
    'zero': '0',
    'period': '.'
}
UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'

headers = {
    'User-Agent': UA
}


# 2、请求网页源代码提取出字体文件的url(http://xxx.woff)及需要转换的十进制数据(&#100064;)。
def get_qd_url(url):
    response = requests.get(url, headers=headers)

    font_url = re.search(re.compile(r"@font-face.*src: url\('(.*?\.woff)'\)", re.S), response.text).group(1)
    num_pattern = re.compile(r'<div class="book-info ">.*?<p>.*?<em>.*?<span class=".*?">(.*?)</span>', re.S)
    data = re.search(num_pattern, response.text).group(1)
    # 3、将要转换的数据去除&#
    numbers = data.split(';')
    num_list = [int(num.replace('&#', '')) for num in numbers if num]

    return num_list, font_url


# 4、请求字体文件的url，获取字体文件的内容
def qd_Font_url(font_url):
    font_response = requests.get(font_url, headers=headers).content
    font = TTFont(io.BytesIO(font_response))
    # 5、获取当前字体映射关系
    map_ele_dict = font.getBestCmap()
    return map_ele_dict


# 6、进行转换得到实际值
def get_real_num(num_list, map_ele_dict, convert_dict):
    result = ''
    for number in num_list:
        # 从字典map_ele_dict中取出对应的one, two, three...
        english_number = map_ele_dict[number]
        # 再以one, two, three...为键，从字典convert_dict中取出数字
        real_number = convert_dict[english_number]
        result += real_number
        # 7、输出真实值
    print("起点某文共{}万字".format(result))


## 猫眼电影 ##
maoyan_font = TTFont('maoyan.woff')  # 加载字体文件
maoyan_table = {'uniE886': '1', 'uniE70F': '9', 'uniE607': '3', 'uniEEDA': '4', 'uniF373': '8',
                'uniE35D': '2', 'uniEAD6': '7', 'uniE198': '0', 'uniE9E8': '6', 'uniF42C': '5'}

# 提取需要替换的文本
maoyan_regex_font = re.compile(r"&#x(.*?);")


def downLoadWoff(text, session):
    """
    下载字体文件
    :param response:
    :return:
    """
    # 从电影详情页面正则提取出woff字体文件
    regexWoff = re.compile(r"url\(\'(.*?\.woff)\'\)")
    woff = regexWoff.search(text).group(1)

    # 请求得到的woff链接地址并下载字体
    woffLink = "http:" + woff
    woffFileName = "font\\" + os.path.basename(woff)

    if not os.path.exists(woffFileName):
        with open(woffFileName, "wb") as file:
            file.write(session.get(url=woffLink).content)

    webfont = TTFont(woffFileName)
    os.remove(woffFileName)

    return webfont


def get_font_number(webfont, text):
    ms = maoyan_regex_font.findall(text)
    for m in ms:
        # mt = hex(int(m))[2:]
        text = text.replace(f'&#x{m};', get_num(webfont, f'uni{m.upper()}'))

    return text


def get_num(webfont, name):
    uni = webfont['glyf'][name]

    for key, value in maoyan_table.items():
        if uni == maoyan_font['glyf'][key]:
            return value


def get_html(url):
    session = requests_html.HTMLSession()
    resp = session.get(url=url, headers=headers)
    # 查看页面内容
    text = resp.html.html
    # 获取票房 用xpath定位输出的是.即提取字体编码的时候不可以用解析库进行解析，改用正则表达式

    # 方式一：解析后还原编码 一次多编码不合适用
    # box_office = resp.html.xpath("//div[@class='movie-index-content box']/span[1]", first=True).text
    # box_office = box_office.encode("unicode_escape").replace(b'\u', b'').decode()
    # print(box_office)
    # 方式二：正则提取
    box_office = \
    re.findall(r'<div class="movie-index-content box">\s*<span class="stonefont">(.*?)</span>', text, re.S)[0]

    # 下载页面字体文件
    web_font = downLoadWoff(text, session)
    real_text = get_font_number(web_font, box_office)
    print("Maoyan After replacing:", real_text)


if __name__ == '__main__':
    qd_url = "https://book.qidian.com/info/1015330582"
    num_list, font_url = get_qd_url(qd_url)
    map_ele_dict = qd_Font_url(font_url)
    get_real_num(num_list, map_ele_dict, convert_dict)
    url = "https://maoyan.com/films/1206605"
    get_html(url)

