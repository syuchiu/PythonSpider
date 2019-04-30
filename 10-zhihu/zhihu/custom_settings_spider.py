"""
@author:hp
@project:10-zhihu
@file:custom_settings_spider.py
@ide:PyCharm
@time:2019/4/29-13:36
"""
custom_settings_for_spider1 = {
    'CONCURRENT_REQUESTS': 100,
    'ITEM_PIPELINES': {
        'zhihu.pipelines.PipelineToCSV': 300,
    },
}
