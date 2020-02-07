from utils.blog_spider.redis_operate_self import RedisOperate
from get_md5 import get_md5

import os
import json
import time
import pymysql
import requests
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
}

db = pymysql.connect(host="localhost", user="root", password='pwd', port=3306, db='sneakerspalace',
                     charset='utf8')
cursor = db.cursor()


def get_response(url):
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.encoding = response.apparent_encoding
    data = response.text
    return data


def get_blog_content(url):
    data = get_response(url)
    soup = BeautifulSoup(data, 'html.parser')
    content = soup.find(class_='content')
    return str(content)


def download_image(image_id, image_url):
    path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    file_path = path + "/media/blog/2020/02/"
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    filename = file_path + image_id + '.jpg'
    urllib.request.urlretrieve(image_url, filename=filename)


def get_blog_info(num):
    index_url = 'http://www.flightclub.cn/mapi/data/news_list_full/' + str(num * 30)
    data = get_response(index_url)
    info_json = json.loads(data)
    redis_operate = RedisOperate()
    temp = 0

    if info_json['ret'] == 'ok':
        print("爬取第" + str(num+1) + "页------------")
        for blog in info_json['msg']['list']:
            blog_url = urljoin(index_url, blog['url'])
            url_md5 = get_md5(blog_url)

            if not redis_operate.duplicate_checking(url_md5):
                blog_id = blog['id']
                blog_title = blog['title']
                print('爬取' + blog_title)
                blog_pic = urljoin(index_url, blog['pic'])
                download_image(blog_id, blog_pic)
                blog_image = 'blog/2020/02/' + blog_id + '.jpg'

                blog_content = get_blog_content(blog_url)
                blog_release_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                params = (blog_id, blog_title, blog_content, blog_image, blog_release_time, datetime.now())

                try:
                    insert_sql = """
                        INSERT INTO blog_blog (`id`, `title`, `content`, `image`, `release_time`, `add_time`) VALUES (%s,%s,%s,%s,%s,%s)
                    """
                    cursor.execute(insert_sql, params)
                    db.commit()
                    redis_operate.put(url_md5)
                    print('爬取' + blog_title + '成功')
                except Exception as e:
                    print(e)
            else:
                temp += 1
                if temp > 5:
                    quit()
                print("重复url,跳过")
                continue


if __name__ == '__main__':
    for i in range(0, 5):
        get_blog_info(i)
        print('休息20秒')
        time.sleep(20)

