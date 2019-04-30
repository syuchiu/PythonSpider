# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhihuItem(scrapy.Item):
    # define the fields for your item here like:
    # type = scrapy.Field()
    question_url = scrapy.Field()  # 问题url
    question_title = scrapy.Field()  # 问题
    answer_url = scrapy.Field()  # 回答url
    answer_content = scrapy.Field()
    answer_voteup_count = scrapy.Field()  # 回答赞同数
    author_url = scrapy.Field()
    author_name = scrapy.Field()  # 回答用户名称
    author_gender = scrapy.Field()  # 回答用户性别
    # user
    answer_count = scrapy.Field()  # 回答数
    follower_count = scrapy.Field()  # 关注者
    name = scrapy.Field()  # 名字
    url_token = scrapy.Field()  # qinlibo_nlp
    url = scrapy.Field()  # 个人信息页链接
    headline = scrapy.Field()
