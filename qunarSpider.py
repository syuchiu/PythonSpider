import random
import time
import codecs
import re
import pymongo

from lxml import etree
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# left 属性设置定位元素左外边距边界与其包含块左边界之间的偏移。
# data-reactid属性是一个自定义属性，因此React可以唯一标识其中的组件。
PATTERN_PRICE_WIDTH = r'<b style="width: (\d+)px;left:-(\d+)px">(\d+)</b>'


class QnrFlight:
    def __init__(self, proxy=None):
        self.url = "https://flight.qunar.com/"
        self.client = pymongo.MongoClient(host='localhost', port=27017)
        self.collection = self.client.qunaer.flights
        chrome_options = ChromeOptions()
        chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--headless')
        # 设置浏览器为开发者模式
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # if proxy:
        #     chrome_options.add_argument('--proxy-server=http://127.0.0.1:8888')

        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.maximize_window()
        self.browser.implicitly_wait(5)  # seconds
        self.wait = WebDriverWait(self.browser, 10)

    def run(self, FromAddr, ToAddr, Sdate):
        self.browser.get(self.url)
        # 判断所需元素是否加载出来
        Dinput = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='dfsForm']/div[2]/div[1]/div/input")))
        Dinput.clear()
        Dinput.send_keys(FromAddr)
        # 进行搜索
        SearchBtn = self.browser.find_element_by_xpath("//*[@id='dfsForm']/div[4]/button")
        time.sleep(self.random_time())
        #
        Ainput = self.browser.find_element_by_xpath("//*[@id='dfsForm']/div[2]/div[2]/div/input")
        Ainput.clear()
        Ainput.send_keys(ToAddr)

        time.sleep(self.random_time())
        # //*[@id="fromDate"]
        DateInput = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='fromDate']")))
        # DateInput = self.browser.find_element_by_xpath("//*[@id='fromDate']").clear()
        DateInput.send_keys(Keys.CONTROL + 'a')
        DateInput.send_keys(Sdate)
        time.sleep(self.random_time())

        SearchBtn.click()
        time.sleep(self.random_time())

        try:
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='mb-10']")))
        except:
            self.browser.refresh()

        while True:
            # 滚动条滑到底部
            scrollJs = "window.scrollTo(0,document.body.scrollHeight)"
            self.browser.execute_script(scrollJs)
            time.sleep(0.5)
            source = self.browser.page_source
            # 获取机票信息
            for item in self.parse_item(source):
                self.save_to_mongodb(item)
            # 判断单页还是多页若多页则翻页
            try:
                isNextPage = self.browser.find_element_by_xpath("//a[text()='下一页']")
                isNextPage.click()
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='mb-10']")))
            except Exception:
                print("已经到尾页")
                self.browser.quit()
                break
        self.get_low_price()

    def parse_item(self, source):
        """
        解析获取数据
        :param source:
        :return:
        """
        root = etree.HTML(source)
        # 定位各航班的节点
        flightNodes = root.xpath("//div[@class='m-airfly-lst']/div[@class='b-airfly']")

        for node in flightNodes:
            item = {}
            # 判断是否需要转机
            trans = node.xpath(".//div[@class='trans']//text()")

            if trans:
                item['FlightNameOne'] = \
                    node.xpath(".//div[@class='col-airline']/div[@class='d-air'][1]/div[@class='air']/span/text()")[0]
                try:
                    item['FlightNameTwo'] = \
                        node.xpath(".//div[@class='col-airline']/div[@class='d-air'][2]/div[@class='air']/span/text()")[
                            0]
                except Exception as error:
                    print(f"同一家航空公司-{item['FlightNameOne']}")

                item['FlightTypeOne'] = ' '.join(
                    node.xpath(".//div[@class='col-airline']/div[@class='d-air'][1]/div[@class='num']//text()"))
                item['FlightTypeTwo'] = ' '.join(
                    node.xpath(".//div[@class='col-airline']/div[@class='d-air'][2]/div[@class='num']//text()"))
                item['Trans'] = ''.join(node.xpath(".//div[@class='trans']//span[@class='t']//text()"))
                # print(f"需要转机:{item['Trans']}")
            else:
                item['FlightName'] = node.xpath(".//div[@class='air']/span/text()")[0]
                item['FlightType'] = ''.join(node.xpath(".//div[@class='num']//text()"))

            item['LeaveTime'] = node.xpath(".//div[@class='sep-lf']/h2/text()")[0]
            item['ArriveTime'] = node.xpath(".//div[@class='sep-rt']/h2/text()")[0]

            priceNode = node.xpath(".//span[@class='prc_wp']")[0]
            priceString = etree.tostring(priceNode).decode()
            fakePrice = priceNode.xpath(".//b/i/text()")
            # 得到总宽度
            PriceWidth = len(fakePrice)
            # 得到字宽和偏移、真实值
            real_price = re.findall(PATTERN_PRICE_WIDTH, priceString)
            # 构造位移字典
            real_price_dict = {int(PriceWidth - int(item[1]) / int(item[0])): item[2] for item in real_price}
            for k, v in real_price_dict.items():
                fakePrice[k] = v
            item['Price'] = ''.join(fakePrice)
            yield item

    def next_page(self):
        """
        进行翻页操作
        :return:
        """
        pass

    def save_to_mongodb(self, item):
        """
        存到数据库
        :return:
        """
        result = self.collection.insert_one(item)

    def get_low_price(self):
        # 查询总量
        count = self.collection.find().count()
        print(f"总机票数为{count}")
        results = self.collection.find({}, {'Price': 1, 'FlightType': 1})

        price_list = [result for result in results]
        price_list.sort(key=lambda item: int(item['Price']))
        print(f"最低价{price_list[0]['FlightType']}--{price_list[0]['Price']}")

    def random_time(self):
        """
        进行随机延时1-3S
        :return:
        """
        return random.uniform(1, 3)


if __name__ == '__main__':
    dcity = input('请输入起点： ')
    acity = input('请输入终点： ')
    date = input('请输入出行日期如"2019-07-06"： ')
    start = time.time()
    air = QnrFlight(proxy=1)
    air.run(dcity, acity, date)
    end = time.time()
    print(f"总耗时{end - start}")
