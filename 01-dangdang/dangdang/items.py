# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


# 只要你的Scrapy Field字段名字和 数据库字段的名字 一样,拷贝这段SQL拼接脚本
class DangdangItem(scrapy.Item):
    # define the fields for your item here like:
    table_name = "dd_info"

    goods_id = scrapy.Field()  # 商品id
    category = scrapy.Field()  # 商品类别
    title = scrapy.Field()  # 商品名称
    link = scrapy.Field()  # 商品链接
    price = scrapy.Field()  # 商品价格
    comments_num = scrapy.Field()  # 商品评论数
    praise_num = scrapy.Field()  # 商品好评数
    # mid_comment_num = scrapy.Field()  # 商品中评数
    negative_num = scrapy.Field()  # 商品差评数
    praise_rate = scrapy.Field()  # 商品的好评率
    source = scrapy.Field()  # 商品的来源地
    detail = scrapy.Field()  # 商品详情
    img_link = scrapy.Field()  # 商品图片链接
    author = scrapy.Field()
    pub = scrapy.Field()
    # pub_time = scrapy.Field()


class CommentItem(scrapy.Item):
    table_name = "dd_comment"
    goods_id = scrapy.Field()  # 商品id
    comment = scrapy.Field()  # 商品的所有评论
    score = scrapy.Field()  # 评论对应的评分
    time = scrapy.Field()  # 评论的时间
