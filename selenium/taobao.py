#!/usr/bin/env python
# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote
from pyquery import PyQuery as pq
import pymongo

'''
wait.until()语句是selenum里面的显示等待，wait是一个WebDriverWait对象，它设置了等待时间，如果页面在等待时间内
没有在 DOM中找到元素，将继续等待，超出设定时间后则抛出找不到元素的异常,也可以说程序每隔xx秒看一眼，如果条件
成立了，则执行下一步，否则继续等待，直到超过设置的最长时间，然后抛出TimeoutException
1.presence_of_element_located 元素加载出，传入定位元组，如(By.ID, 'p')
2.element_to_be_clickable 元素可点击
3.text_to_be_present_in_element 某个元素文本包含某文字
'''
#定义一个浏览器
browser = webdriver.Chrome()
#定义一个无界面浏览器
# browser = webdriver.Chrome(
#     service_args=[
#             '--load-images=false',
#             '--disk-cache=true'])
#如果10s无响应就down掉
wait = WebDriverWait(browser,10)
#定义窗口大小（无界面也需要定义）
browser.set_window_size(1400,900)
KEYWORD = 'iPad'


def index_page(page):
    """
    抓取索引页
    :param page:页码
    :return:
    """
    print('正在爬取第',page,'页')
    try:
        url = 'https://search.jd.com/Search?keyword=' + quote(KEYWORD)
        browser.get(url)
        if page > 1:
            #选择淘宝首页的输入框
            input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR,'#miansrp-pager div.form > input')))
            submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#mainsrp-pager div-form > span.btn.J_Submit')))
            input.clear()
            input.send_keys(page)
            submit.click()
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#mainsrp-pager li.iyem.active > span'),str(page)))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.m-itemlist .items .item')))
        get_products()
    except TimeoutException:
        index_page(page)

def get_products():
    """
    提取商品数据
    :return:
    """
    html = browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .items').items()
    for item in items:
        product = {
            'image':item.find('.pic .img').attr('data-src'),
            'price':item.find('.price').text(),
            'deal':item.find('.deal-cnt').text(),
            'title':item.find('.title').text(),
            'shop':item.find('.shop').text(),
            'location':item.find('.location').text()
        }
        print(product)
        save_to_mongo(product)

MONGO_URL = 'localhost'
MONGO_DB = 'taobao'
MONGO_COLLECTION = 'products'
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]


def save_to_mongo(result):
    """
    保存至MongoDB
    :param result:结果
    :return:
    """
    try:
        if db[MONGO_COLLECTION].insert(result):
            print('存储到MongoDB成功')
    except Exception:
        print('存储到MongoDB失败')

MAX_PAGE = 10
def main():
    """
    遍历每一页
    :return:
    """
    for i in range(1,MAX_PAGE +1):
        index_page(i)

if __name__ == '__main__':
    main()
