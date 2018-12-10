#!/usr/bin/env python
# -*- coding:utf-8 -*-
import requests
import re
import json



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
    for item in items:
        yield{
            'index':item[0],
            'image':item[1],
            'title':item[2].strip(),
            'actor':item[3].strip(),
            'time':item[4].strip(),
            'score':item[5].strip() + item[6].strip()
        }

def write_to_file(content):
    with open('maoyan_top.txt','a',encoding='utf-8')as f:  #参数'a'表示追加
        # print(type(json.dumps(content)))
        f.write(json.dumps(content,ensure_ascii=False) +'\n')


def main():
    url = 'http://maoyan.com/board/4'
    html = get_one_page(url)
    for item in parse_one_page(html):
        write_to_file(item)
if __name__ == '__main__':
    main()