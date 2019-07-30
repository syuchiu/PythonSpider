"""
@file:Qilogin.py
@time:2019/7/29-17:19
"""
import logging
import pickle
import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def QiSelenium(index_url, telephone, cookies=None):
    chrome_options = webdriver.ChromeOptions()
    # 添加启动参数
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--start-maximized')
    # chrome_options.add_argument('--proxy-server={0}'.format(PROXY))
    # chrome_options.add_argument('window-size=1920x3000')  # 指定浏览器分辨率
    chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    # chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
    # 添加实验性质的设置参数
    # chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    browser = webdriver.Chrome(chrome_options=chrome_options)
    # browser.maximize_window()
    wait = WebDriverWait(browser, 10)
    browser.get(index_url)
    if cookies is not None:
        for cookie in cookies:
            browser.add_cookie(cookie)
        browser.refresh()
    else:
        try:
            btnclick = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='app-login f-hblue']")))
            btnclick.click()
            print("-----" * 10)
            time.sleep(3)
            # handbtn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class='hand']")))
            handbtn = browser.find_element_by_xpath("//div[@class='footer-logiin']")
            # handbtn.screenshot("code2.png")
            # browser.get_screenshot_as_file("qmp.png")
            actions = ActionChains(browser)
            actions.move_to_element(handbtn).click().perform()
            input_phone = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@class='c-phone-input']")))
            input_phone.send_keys(telephone)
            codebtn = browser.find_element_by_xpath("//button[@class='c-code-btn']")
            codeinput = browser.find_element_by_xpath("//input[@class='c-code-input']")
            codesubmit = browser.find_element_by_xpath("//button[@class='c-submit-btn']")
            codebtn.click()
            code = input("输入验证码:")
            codeinput.send_keys(code)
            codesubmit.click()
        except Exception as e:
            logging.warning("click error")
            logging.warning(e)
    time.sleep(3)
    try:
        text = browser.find_element_by_xpath("//span[@class='fs12 fc3 ml2']").text
    except:
        print("没找到登陆后的标识")
        text = ""
    # 判断登录是否成功,若成功则保存并返回cookie
    if "充值" in text:
        print("登录成功")
        # 保存 Cookies
        pickle.dump(browser.get_cookies(), open("cookies.pkl", "wb"))
        cookies = browser.get_cookies()
        browser.quit()
        return cookies
    else:
        browser.quit()
        return None

