"""
@file:city_and_car.py
@time:2019/5/29-23:48
"""
import base64
import io
import re

import pytesseract
import requests
from PIL import Image
from fontTools.ttLib import TTFont
from fake_useragent import UserAgent
from scrapy import Selector

# 58同城
from selenium import webdriver


class Font58Mapping(object):
    def __init__(self, response):
        self.response = response
        self.standard_ttf = 'city_standard_font.ttf'
        # 选定作为基准字体的Unicode编码和对应文字
        self.word_tuple = ['博', '2', '硕', '李', '验', '张', '4', '男', '0', '本', '陈', '校', '5',
                           '7', '士', 'E', '杨', '枝', '届', '黄', '高', '周', '以', '女', '8', '无', '专',
                           '吴', '科', 'M', '下', '中', '1', '生', '王', '3', '6', 'B', '经', '大', 'A', '刘',
                           '赵', '应', '9']

    @staticmethod
    def get_font_coordinate_list(font_obj, uni_list):
        """
        获取字体文件的坐标信息列表
        :param font_obj: 字体文件对象
        :param uni_list: 总体文件包含字体的编码列表或元祖
        :return: 字体文件所包含字体的坐标信息列表
        """
        font_coordinate_list = []

        for uni in uni_list:
            # 每一个字的GlyphCoordinates对象，包含所有文字连线位置坐标（x,y）元组信息
            word_glyph = font_obj['glyf'][uni].coordinates
            # 转化为列表
            coordinate_list = list(word_glyph)
            # 汇总所有文字坐标信息
            font_coordinate_list.append(coordinate_list)

        return font_coordinate_list

    @staticmethod
    def comparison(coordinate1, coordinate2):
        """
        对比单个新字体和基准字体的坐标值，若全部相等则返回True，否则False
        :param coordinate1: 单字体1的坐标信息
        :param coordinate2: 单字体2的坐标信息
        :return: True或False
        """
        if len(coordinate1) != len(coordinate2):
            return False
        for i in range(len(coordinate1)):
            # 对比坐标元组是否相等
            if coordinate1[i] == coordinate2[i]:
                pass
            else:
                return False
            return True

    def get_font_content(self):
        """
        :return:匹配获取原始自定义字体的二进制文件内容
        """
        new_font_url = re.search(r'base64,(.*?)\)', self.response, re.S).group(1)
        font_data_after_decode = base64.b64decode(new_font_url)

        return font_data_after_decode

    # 对比新字体文件和已手工提取的基准字体文件对比
    def get_new_font_dict(self):
        """
        用初始化的传入的基准字体和新字体文件对比，得到新字体文件编码与真实文字的映射。
        :return: 新字体文件中原编码与实际文字的映射字典
        """
        standard_font = TTFont(self.standard_ttf)
        # 获取基准字体坐标库
        uni_tuple = standard_font.getGlyphOrder()[2:]
        # print("uni1:", uni_tuple, len(uni_tuple))
        standard_coordinate_list = self.get_font_coordinate_list(standard_font, uni_tuple)
        # 下载获取当前自定义字体的二进制文件
        b_font = self.get_font_content()
        # 将二进制文件当做文件操作
        new_font = TTFont(io.BytesIO(b_font))
        # 读取新字体坐标,去除第一个空值
        uni_list2 = new_font.getGlyphOrder()[2:]
        # print("uni2:", uni_list2, len(uni_list2))

        # 获取新字体坐标库
        new_coordinate_list = self.get_font_coordinate_list(new_font, uni_list2)
        new_font_dict = {}
        # 比较基准字体和新字体坐标，映射新字体对应文字
        for nc_index, ncd in enumerate(new_coordinate_list):

            for sc_index, scd in enumerate(standard_coordinate_list):
                # 若相等构造新的对造表
                if self.comparison(scd, ncd):
                    new_font_dict[uni_list2[nc_index]] = self.word_tuple[sc_index]

        return new_font_dict

    # 替换原始response中的编码内容为真实值,返回新的response内容
    def replace_response_font(self):
        new_font_dict = self.get_new_font_dict()

        new_response = self.response

        for key, value in new_font_dict.items():
            # 此替换方式仅建立在 <map code="0xe021" name="uniE021"/>,对起点中文网不适用
            key_ = key.lower().replace('uni', "&#x") + ";"
            # 替换原网页中所有对应的key为实际数值value
            if key_ in self.response:
                new_response = new_response.replace(key_, str(value))

        return new_response

    # 由实例调用
    def __call__(self):
        return self.replace_response_font()


# 汽车之家
class CarHomeFontMapping:
    def __init__(self, response):
        self.response = response
        self.standard_font_obj = 'car_standard_font.ttf'

        self.word_tuple = ('二', '一', '七', '呢', '八', '是', '矮', '短', '大', '十',
                           '很', '低', '多', '五', '地', '左', '小', '更', '近', '上',
                           '好', '右', '高', '和', '长', '六', '下', '得', '三', '坏',
                           '少', '四', '着', '远', '了', '不', '的', '九')

    @staticmethod
    def get_font_coordinate_list(font_obj, uni_list):
        """
        获取字体文件的坐标信息列表
        :param font_obj: 字体文件对象
        :param uni_list: 总体文件包含字体的编码列表或元祖
        :return: 字体文件所包含字体的坐标信息列表
        """
        font_coordinate_list = []
        for uni in uni_list:
            # 每一个字的GlyphCoordinates对象，包含所有文字连线位置坐标（x,y）元组信息
            word_glyph = font_obj['glyf'][uni].coordinates
            # 转化为列表
            coordinate_list = list(word_glyph)
            # 汇总所有文字坐标信息
            font_coordinate_list.append(coordinate_list)

        return font_coordinate_list

    @staticmethod
    def comparison(coordinate1, coordinate2):
        """
        对比单个新字体和基准字体的坐标差值，若差值在设定范围变化则返回True，否则False
        :param coordinate1: 单字体1的坐标信息
        :param coordinate2: 单字体2的坐标信息
        :return: True或False
        """
        if len(coordinate1) != len(coordinate2):
            return False
        for i in range(len(coordinate1)):
            if abs(coordinate1[i][0] - coordinate2[i][0]) < 50 and abs(coordinate2[i][1] - coordinate2[i][1]) < 50:
                pass
            else:
                return False

            return True

    def get_font_content(self):
        """
        :return:原始自定义字体的二进制文件内容
        """
        new_font_url = re.findall(r"@font-face.*?,url\('(.*?)'\) format", self.response, re.S)
        print("new_font_url:", new_font_url)
        b_font = requests.get("https:" + new_font_url[0]).content
        return b_font

    # 对比新字体文件和已手工提取的基准字体文件对比
    def get_new_font_dict(self):
        """
        用初始化的传入的基准字体和新字体文件对比，得到新字体文件编码与真实文字的映射。
        :return: 新字体文件中原编码与实际文字的映射字典
        """
        standard_font = TTFont(self.standard_font_obj)
        uni_tuple = standard_font.getGlyphOrder()[1:]
        # 获取基准字体坐标库
        standard_coordinate_list = self.get_font_coordinate_list(standard_font, uni_tuple)
        # print("old:", standard_coordinate_list)
        # 下载获取当前自定义字体的二进制文件
        b_font = self.get_font_content()
        # 将二进制文件当做文件操作
        new_font = TTFont(io.BytesIO(b_font))
        # 读取新字体坐标,去除第一个空值
        uni_list2 = new_font.getGlyphOrder()[1:]
        # 获取新字体坐标库
        new_coordinate_list = self.get_font_coordinate_list(new_font, uni_list2)
        # print("new:", new_coordinate_list)

        new_font_dict = {}
        # 比较基准字体和新字体坐标，映射新字体对应文字
        for nc_index, ncd in enumerate(new_coordinate_list):
            for sc_index, scd in enumerate(standard_coordinate_list):

                if self.comparison(scd, ncd):
                    new_font_dict[uni_list2[nc_index]] = self.word_tuple[sc_index]

        return new_font_dict

    def replace_response_font(self):
        new_font_dict = self.get_new_font_dict()
        new_response = self.response
        print("new_font:", new_font_dict)

        for key, value in new_font_dict.items():
            print(key, value)
            key_ = key.lower().replace('uni', "<span style='font-family: myfont;'>&#x") + ';</span>'
            # key_ = key.lower().replace('uni', "&#x") + ';'
            # 替换原网页中所有对应的key为实际数值value
            if key_ in self.response:
                new_response = new_response.replace(key_, str(value))

        return new_response

    def __call__(self):
        return self.replace_response_font()


# 利用OCR识别
class FontOCR:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('blink-settings=imagesEnabled=false')
        self.browser = webdriver.Chrome(chrome_options=chrome_options)

    def get_html(self, url):
        self.browser.get(url)
        # screenshot元素截图
        myshot = self.browser.find_element_by_xpath("//div[@class='tz-paragraph']")
        # print(myshot.get_attribute('outerHTML'))
        myshot.screenshot("myshot.png")
        image = Image.open('myshot.png')
        # image = image.convert('L')
        # threshold = 80
        # table = []
        # for i in range(256):
        #     if i < threshold:
        #         table.append(0)
        #     else:
        #         table.append(1)
        #
        # image = image.point(table, '1')
        # image.show()
        text = pytesseract.image_to_string(image, lang='chi_sim')

        print(text.replace("\n", "").strip())


if __name__ == '__main__':
    # 调用UserAgent类生成ua实例
    ua = UserAgent()
    # ua实例调用random方法随机返回一个ua字符串
    headers = {
        'user-agent': ua.random,
    }
    # 58同城测试
    # city_url = "https://su.58.com/qztech/"
    # resp = requests.get(city_url, headers=headers, verify=False).text
    # mycity = Font58Mapping(resp)
    # mapping = mycity.get_new_font_dict()
    # content = mycity()
    # node = Selector(text=content)
    # name = node.xpath("//span[contains(@class,'stonefont ')]/text()").extract_first()
    # print(name)
    # 汽车之家测试
    car_url = "https://club.autohome.com.cn/bbs/thread/1bffedd751791ced/78354121-1.html"
    # response = requests.get(car_url, headers=headers).text
    # new_font_dict = CarHomeFontMapping(response)
    # print(new_font_dict())
    font = FontOCR()
    font.get_html(car_url)
