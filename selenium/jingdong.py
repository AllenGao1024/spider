#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import pymongo
import re
from pyquery import PyQuery as pq
from bs4 import BeautifulSoup

from lxml import etree
# 定义一个浏览器
# browser = webdriver.Chrome()
# 定义一个无界面的浏览器
browser = webdriver.PhantomJS(
    service_args=[
        '--load-images=false',
        '--disk-cache=true'])
# 50s无响应就down掉
wait = WebDriverWait(browser, 50)
#定义一个窗口大小（无界面也需要定义）
browser.set_window_size(1400,900)


def search():
    """
    此函数的作用为完成首页点击搜索的功能，替换标签可用于其他网页使用
    :return:
    """
    #访问页面
    browser.get('https://www.jd.com/')
    try:
        #选择到京东首页的输入框
        input = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#key"))
        )  # llist
        #搜索的按钮
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#search > div > div.form > button"))
        )
        # input = browser.find_element_by_id('key')
        #send_key作为写到input的内容
        input[0].send_keys('python')
        #执行点击搜索的操作
        submit.click()
        #查看当前页码一共有多少页
        total = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > em:nth-child(1) > b')
            )
        )
        #获取所有商品
        get_products()
        #返回总页数
        return total[0].text

    except TimeoutError:
        return search()


def next_page(page_number):
    """
    翻页函数
    :param page_number:
    :return:
    """
    print('正在翻页', '第' + str(page_number) + '页')
    try:
        # 滑动到底部，加载出后三十个货物信息
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10)
        # 翻页动作
        button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_bottomPage > span.p-num > a.pn-next > em'))
        )
        button.click()
        wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#J_goodsList > ul > li:nth-child(60)"))
        )

        # 判断翻页成功
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#J_bottomPage > span.p-num > a.curr"), str(page_number))
        )
        # 获取所有商品
        get_products()
    except TimeoutError:
        return next_page(page_number)


# 提取网页的图片的网址
# def parse_html_page(html):
#     # 对有效图片网址进行提取
#     soup = BeautifulSoup(html, 'lxml')
#     # 定义一个列表来获取分析得到的图片的网址
#
#     url_items = []
#     li_tags = soup.find_all('li', 'gl-item')
#     for li_tag in li_tags:
#         try:
#             if len(li_tag.img["src"]) >= 10:
#                 url_items.append("http:"+ li_tag.img['src'])
#             else:
#                 pass
#         except:
#             if len(li_tag.img["data-lazy-img"]) >= 10:
#                 url_items.append("http:"+ li_tag.img['data-lazy-img'])
#             else:
#                 url_items.append("http:"+ li_tag.img["src"])
#     return url_items



def get_products():
    """
    提取商品数据
    :return:
    """

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#J_goodsList .gl-item")))
    #拿到整个页面的源代码
    html = browser.page_source
    #pq解析网页源代码
    doc = pq(html)
    items = doc('#J_goodsList .gl-item').items()
    for item in items:
        product = {
            'title': item.find('.p-name').text(),
            'price': item.find('.p-price').text(),
            'image': 'https:'+ str(item.find('.p-img a img').attr('data-lazy-img',)), #发现img在data-lazy-img中居多
            'src': 'https:'+ str(item.find('.p-img a img').attr('src',)),
            'commit': item.find('.p-commit').text(),
            'shop': item.find('.curr-shop').text(),
        }
        print(product)
        save_to_mongo(product)


MONGO_URL = 'localhost'
MONGO_DB = 'jingdong'
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



def main():
    # try:
        # 第一步搜索
        print("第", 1, "页：")
        total = int(search())
        # int类型刚才找到的总页数标签，作为跳出循环的条件
        # total = int(re.compile('(\d+)').search(total).group(1))
        # 只要后面还有就继续爬，继续翻页
        for i in range(2, total + 1):
            time.sleep(3)
            print("第", i, "页：")
            next_page(i)
    # except Exception:
    #     print('出错啦')
    # finally:
    #     # 关闭浏览器
    #     browser.close()


if __name__ == "__main__":
    main()