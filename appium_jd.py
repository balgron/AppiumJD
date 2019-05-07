#!usr/bin/env python3
# -*- coding: utf-8 -*-
# 功能：爬取商品信息

from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from selenium.common.exceptions import NoSuchElementException
from pymongo import MongoClient

DRIVER_SERVER = 'http://localhost:4723/wd/hub'
TIMEOUT = 30
KEYWORD = 'iPad'
FLICK_STRAT_X = 300
FLICK_START_Y = 300
FLICK_DISTANCE = 700
SCROLL_SLEEP_TIME = 1
MONGODB_URL = 'localhost'
MONGODB_DB = 'products'
MONGODB_COLLECTION = 'iPad'

class Product():
    def __init__(self):
        # 驱动配置
        self.desired_caps = {
            'platformName': 'Android',
            'deviceName': 'OPPO_R11',
            'appPackage': 'com.jingdong.app.mall',
            'appActivity': 'main.MainActivity'
        }
        self.driver = webdriver.Remote(DRIVER_SERVER, self.desired_caps)
        self.wait = WebDriverWait(self.driver, TIMEOUT)
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client[MONGODB_DB]
        self.collection = self.db[MONGODB_COLLECTION]

    def enter(self):
        # 对于不同平台和版本来说，可能不会完全一致
        # 点击欢迎页
        el1 = self.driver.find_element_by_id('com.jingdong.app.mall:id/bnm')
        el1.click()
        # 允许访问通话
        el2 = self.driver.find_element_by_id('com.android.packageinstaller:id/permission_allow_button')
        el2.click()
        # 允许访问位置信息
        el3 = self.driver.find_element_by_id('com.android.packageinstaller:id/permission_allow_button')
        el3.click()
        sleep(2)
        # ×掉礼品包
        el4 = self.driver.find_element_by_id('com.jingdong.app.mall:id/bgp')
        el4.click()
        print('登录成功')
        # 点击搜索框
        el5 = self.driver.find_element_by_id('com.jingdong.app.mall:id/a49')
        el5.click()
        # 搜索框输入iPad
        el6 = self.driver.find_element_by_accessibility_id('搜索框,吃货嘉年华')
        el6.set_text(KEYWORD)
        # 点击搜索
        el7 = self.driver.find_element_by_id('com.jingdong.app.mall:id/au5')
        el7.click()
        print('进入商品列表')

    def scroll(self):
            # 模拟拖动
            self.driver.swipe(FLICK_STRAT_X, FLICK_START_Y + FLICK_DISTANCE, FLICK_STRAT_X, FLICK_START_Y)
            sleep(SCROLL_SLEEP_TIME)

    def parse_items(self):
        # 解析商品名，价格，店名
        print('开始爬取商品信息')
        while True:
            # 直接使用Appium提供的xpath路径
            items = self.wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, '/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.'
                           'FrameLayout/android.support.v4.widget.DrawerLayout/android.view.ViewGroup/android.'
                           'support.v7.widget.RecyclerView/android.widget.RelativeLayout')))
            # 遍历每条商品信息
            for item in items:
                try:
                    name = item.find_element_by_id('com.jd.lib.search:id/a2a').get_attribute('text')
                    price = item.find_element_by_id('com.jd.lib.search:id/a2g').get_attribute('text')
                    shop = item.find_element_by_id('com.jd.lib.search:id/agl').get_attribute('text')
                    data = {
                        'name': name,
                        'price': price,
                        'shop': shop
                    }
                    print(data)
                    # 插入数据库，去重
                    self.collection.update({'name': name}, {'$set': data}, True)
                except NoSuchElementException:
                    pass
            self.scroll()


    def main(self):
        self.enter()
        self.parse_items()

if __name__ == '__main__':
    product = Product()
    product.main()
