#!/usr/bin/env python
# -*- coding:utf-8 -*-
import requests
from urllib.parse import urlencode
import os
from hashlib import md5
from multiprocessing.pool import Pool

base_url = 'https://www.toutiao.com/search_content/?'


def get_page(offset):
    params = {
        'offset': offset,
        'format': 'json',
        'keyword': 'NBA',
        'autoload': 'true',
        'count':'20',
        'cur_tab':'1',
        'from':'search_tab',
        'pd':'synthesis'
    }

    url = base_url + urlencode(params)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError:
        return None


def get_images(json):
    if json.get('data'):
        for item in json.get('data'):
            title = item.get('title')
            images = item.get('image_list')
            if images is not None:
                for image in images:
                    yield{
                        'image': image.get('url'),
                        'title': title,
                    }


def save_image(item):
    if not os.path.exists("images/" + item.get('title')):
        os.makedirs("images/" + item.get('title'))
    try:
        response = requests.get('http:'+ item.get('image'))
        if response.status_code == 200:
            file_path = '{0}/{1}/{2}.{3}'.format('images', item.get('title'),md5(response.content).hexdigest(),'jpg')
            if not os.path.exists(file_path):
                with open(file_path,'wb')as f:
                    f.write(response.content)
    except requests.ConnectionError:
        print('Fail to save Image')

def main(offset):
    json = get_page(offset)
    for item in get_images(json):
        print(item)
        save_image(item)


GROUP_START = 1
GROUP_END = 10

if __name__ == '__main__':
    pool = Pool()
    groups = ([x * 5 for x in range(GROUP_START,GROUP_END + 1)])
    pool.map(main, groups)
    pool.close()
    pool.join()