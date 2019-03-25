from scrapy import cmdline

cmdline.execute("scrapy crawl DD".split())
# lpush DD:start_urls http://category.dangdang.com/