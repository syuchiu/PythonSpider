import re
import requests
import time

import scrapy
from lxml import etree

from scrapy_redis.spiders import RedisSpider

from dangdang.items import DangdangItem, CommentItem


def url_is_legal(url):
    if url == "javascript:void(0);":
        return False
    if url == "":
        return False
    return True


class DangDangSpider(RedisSpider):
    name = "DD"
    # redis_key是爬虫名字加冒号加start_urls,所有的爬虫都是从redis来获取url
    # If empty, uses default '<spider>:start_urls'
    redis_key = 'DD:start_urls'
    allowed_domains = ["dangdang.com"]

    # start_urls = ['http://category.dangdang.com/']

    def __init__(self, *args, **kwargs):
        # 修改这里的类名为当前类名
        super(DangDangSpider, self).__init__(*args, **kwargs)

    # def start_requests(self):
    #     yield scrapy.Request(url=self.start_urls[0], callback=self.parse)

    def parse(self, response):
        item_list = response.xpath("//div[@class = 'classify_kind']//a/@href").extract()
        for href in item_list:
            yield scrapy.Request(href, callback=self.parse_nxt)

    # 二级页面解析列表页
    def parse_nxt(self, response):
        li_list = response.xpath("//div[@id = 'search_nature_rg']/ul[1]/li")

        for li in li_list:
            item = DangdangItem()
            item["link"] = li.xpath("./a[1]/@href").extract_first()
            item["title"] = li.xpath("./a[1]/@title").extract_first().strip()

            item["img_link"] = li.xpath("./a[1]/img/@data-original").extract_first()
            if not item["img_link"]:
                item["img_link"] = li.xpath("./a[1]/img/@src").extract_first()

            try:
                price = li.xpath("./p[@class = 'price']/span/text()").extract()[0]
            except:
                price = li.xpath("./p[@class = 'price']/span/text()").extract()[1]

            item['price'] = price.replace('¥', '')
            # 商品详情
            item["detail"] = li.xpath("./p[@class = 'detail']//text()").extract_first()
            if not item["detail"]:
                item["detail"] = li.xpath("./p[@class = 'search_hot_word']//text()").extract_first()
            # 评论数
            item["comments_num"] = li.xpath("./p[@class = 'search_star_line']//a/text()").extract_first()
            if not item["comments_num"]:
                item["comments_num"] = li.xpath("./p[@class = 'star']//a/text()").extract_first()
            # 作者
            item["author"] = li.xpath("./p[@class = 'search_book_author']/span[1]/a/text()").extract_first()
            # 出版社
            item["pub"] = li.xpath("./p[@class = 'search_book_author']/span[3]/a/text()").extract_first()
            # 出版时间
            if url_is_legal(item["link"]):
                yield scrapy.Request(item["link"], callback=self.parse_details, meta={"item": item})

        time.sleep(1)
        nxt_tmp = response.xpath("//div[@class = 'paging']//li[@class = 'next']/a/@href").extract_first()
        if nxt_tmp is not None:
            nxt_page = "http://category.dangdang.com" + nxt_tmp
            yield scrapy.Request(nxt_page, callback=self.parse_nxt)

    # 详情页面解析
    def parse_details(self, response):
        commment_item = CommentItem()
        item = response.meta["item"]
        # 商品所属类别
        item["category"] = response.xpath('//*[@id="breadcrumb"]/a[1]/b/text()').extract_first() + '>' + response.xpath(
            '//*[@id="breadcrumb"]/a[2]/text()').extract_first() + '>' + response.xpath(
            '//*[@id="breadcrumb"]/a[3]/text()').extract_first()
        # 商品来源
        try:
            item["source"] = response.xpath("//*[@id='shop-geo-name']/text()").extract()[0].replace('\xa0至', '')
        except IndexError as e:
            item["source"] = '当当自营'

        # 通过正则表达式提取url中的商品id
        goodsid = re.compile('\/(\d+).html').findall(response.url)[0]
        commment_item['goods_id'] = goodsid
        item["goods_id"] = goodsid

        # 提取详情页源码中的categoryPath
        script = response.xpath("/html/body/script[1]/text()").extract()[0]
        categoryPath = re.compile(r'.*categoryPath":"(.*?)","describeMap').findall(script)[0]
        # 构造包含好评率包的链接
        url = "http://product.dangdang.com/index.php?r=comment%2Flist&productId=" + str(
            goodsid) + "&categoryPath=" + str(categoryPath) + "&mainProductId=" + str(goodsid)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
        resp = requests.get(url, headers=headers)
        data_dict = resp.json()
        item["praise_rate"] = data_dict['data']['list']['summary']['goodRate']
        # 获取好评数
        item["praise_num"] = data_dict['data']['list']['summary']['total_crazy_count']
        # 获取差评数
        item["negative_num"] = data_dict['data']['list']['summary']['total_detest_count']
        yield item

        # 通过接口存储评论
        html_str = data_dict['data']['list']['html']
        html = etree.HTML(html_str)
        comment_items = html.xpath('//div[@class="comment_items clearfix"]')
        pageIndex = 1
        while comment_items:
            pageIndex += 1

            for item in comment_items:
                comment_unit = item.xpath('.//div[@class="describe_detail"][1]/span[not(@class="icon")]/text()')
                score = item.xpath('.//div[@class="pinglun"]/em/text()')[0]
                time = item.xpath('.//div[@class="items_right"]/div[@class="starline clearfix"][1]/span[1]/text()')[0]
                comment = ' '.join(comment_unit)
                commment_item["comment"] = comment
                commment_item['score'] = score
                commment_item["time"] = time
                yield commment_item

            rate_url = "http://product.dangdang.com/index.php?r=comment%2Flist&productId=" + str(
                goodsid) + "&categoryPath=" + str(categoryPath) + "&mainProductId=" + str(
                goodsid) + "&pageIndex=" + str(pageIndex)
            # 页数超出范围则显示其余用户默认好评
            r = requests.get(rate_url, headers=headers)
            data_dict = r.json()
            html_str = data_dict['data']['list']['html']
            html = etree.HTML(html_str)
            comment_items = html.xpath('//div[@class="comment_items clearfix"]')
