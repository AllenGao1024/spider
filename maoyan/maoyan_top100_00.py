#!/usr/bin/env python
# -*- coding:utf-8 -*-
import requests
import re



def get_one_page(url):
    headers = {
        'User-Agent':'Mozilla/5.0(Macintosh;Intel Mac OS X 10_13_3)AppleWebKit/537.36(KHTML,like Gecko)Chrome/70.0.3538.77 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    return None


def parse_one_page(html):
    pattern = re.compile('<dd>.*?board-index.*?>(\d*)</i>.*?data-src="(.*?)".*?name"><a.*?>(.*?)</a>.*?star">'
                         + '(.*?)</p>.*?releasetime">(.*?)</p>'
                         + '.*?integer">(.*?)</i>.*?fraction">(.*?)</i></p>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    print(items)

def main():
    url = 'http://maoyan.com/board/4'
    html = get_one_page(url)
    parse_one_page(html)
if __name__ == '__main__':
    main()