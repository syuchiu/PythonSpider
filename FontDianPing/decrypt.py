"""
@file:decrypt.py
@time:2019/6/11-10:01
"""
import re

from constants import PATTERN_SVG_TEXT


def _decrypt_woff_tag(unitext, dictionary):
    """
    解析自定义字体
    :param node:
    :param dictionary:
    :return:
    """
    for key, value in dictionary.items():
        # ef44 in unief44
        if unitext in key:
            return value


def _decrypt_text_tag(svg_content, font_size, x_offset, y_offset):
    """
    :param svg_content:
    :param font_size:
    :param x_offset:
    :param y_offset:
    :return:
    """
    pattern = re.compile(PATTERN_SVG_TEXT, re.S)

    items = re.findall(pattern, svg_content)

    svg_lists = [{'y_key': int(item[0]), 'text': item[1]} for item in items]

    for svg in svg_lists:
        if svg['y_key'] < y_offset:
            continue

        return svg['text'][x_offset // font_size]


def _decrypt_textPath_tag(svg_content, font_size, x_offset, y_offset):
    y = re.findall(r'id="\d+" d="\w+\s(\d+)\s\w+"', svg_content, re.M)
    words = re.findall(r'" textLength.*?(\w+)</textPath>', svg_content, re.M)

    svg_lists = list(zip(y, words))

    for svg in svg_lists:
        if int(svg[0]) < y_offset:
            continue

        return svg[1][x_offset // font_size]
