import execjs
import requests
import json
import pymysql
from datetime import datetime
import urllib.request
import os
import threading
import queue
from redis_operate import RedisOperate

headers = {
    'Host': "app.poizon.com",
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.4.501 NetType/WIFI "
                  "MiniProgramEnv/Windows WindowsWechat",
    'appid': "wxapp",
    'appversion': "4.4.0",
    'content-type': "application/x-www-form-urlencoded",
    'Accept-Encoding': "gzip, deflate",
    'Accept': "*/*",
}
redis_operate = RedisOperate()


def download_image(articleNumber, image_url):
    file_path = "F:/PycharmProjects/SneakerPalace/media/sneakers/2020/01/"
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    filename = file_path + articleNumber + '.jpg'
    urllib.request.urlretrieve(image_url, filename=filename)


def get_recensales_list_url(lastId, productId):
    # 最近购买接口
    with open('sign.js', 'r', encoding='utf-8')as f:
        all_ = f.read()
        ctx = execjs.compile(all_)
        sign = ctx.call('getSign',
                        'lastId{}limit20productId{}sourceAppapp19bc545a393a25177083d4a748807cc0'.format(lastId,
                                                                                                        productId))
        recensales_list_url = 'https://app.poizon.com/api/v1/h5/product/fire/recentSoldList?' \
                              'productId={}&lastId={}&limit=20&sourceApp=app&sign={}'.format(productId, lastId, sign)
        return recensales_list_url


def get_search_by_keywords_url(page, sortMode, sortType):
    # 关键词搜索商品接口
    with open('sign.js', 'r', encoding='utf-8')as f:
        all_ = f.read()
        ctx = execjs.compile(all_)
        # 53489
        sign = ctx.call('getSign',
                        'limit20page{}sortMode{}sortType{}titleajunionId19bc545a393a25177083d4a748807cc0'.format(page,
                                                                                                                 sortMode,
                                                                                                                 sortType))
        search_by_keywords_url = 'https://app.poizon.com/api/v1/h5/product/fire/search/list?title=aj&page={}&sortType={}&sortMode={}&' \
                                 'limit=20&unionId=&sign={}'.format(page, sortType, sortMode, sign)
        return search_by_keywords_url


def get_brand_list_url(lastId, tabId):
    # 商品品类列表接口
    with open('sign.js', 'r', encoding='utf-8')as f:
        all_ = f.read()
        ctx = execjs.compile(all_)
        sign = ctx.call('getSign',
                        'lastId{}limit20tabId{}19bc545a393a25177083d4a748807cc0'.format(lastId, tabId))
        brand_list_url = 'https://app.poizon.com/api/v1/h5/index/fire/shoppingTab?' \
                         'tabId={}&limit=20&lastId={}&sign={}'.format(tabId, lastId, sign)
        return brand_list_url


def get_product_detail_url(productId):
    # 商品详情接口
    with open('sign.js', 'r', encoding='utf-8')as f:
        all_ = f.read()
        ctx = execjs.compile(all_)
        sign = ctx.call('getSign',
                        'productId{}productSourceNamewx19bc545a393a25177083d4a748807cc0'.format(productId))
        product_detail_url = 'https://app.poizon.com/api/v1/h5/index/fire/flow/product/detail?' \
                             'productId={}&productSourceName=wx&sign={}'.format(productId, sign)
        return product_detail_url


def isFloat(value):
    try:
        float(value)
        return True
    except:
        return False


def get_product_detail():
    db = pymysql.connect(host="localhost", user="root", password='pwd', port=3306, db='sneakerspalace',
                         charset='utf8')
    cursor = db.cursor()

    while not q.empty():
        productId = q.get()
        size_info = []
        product_detail_url = get_product_detail_url(productId)
        product_detail_response = requests.get(product_detail_url, headers=headers)
        product_detail_json = json.loads(product_detail_response.text)
        if product_detail_json['msg'] == 'ok':
            if not isFloat(product_detail_json['data']['sizeList'][0]['size']):
                continue
            name = product_detail_json['data']['detail']['title']
            if 'jordan' in name.lower() or 'yeezy' in name.lower() or 'adidas' in name.lower() or 'nike' in name.lower():
                if 'jordan' in name.lower():
                    brand = "Jordan"
                elif 'nike' in name.lower():
                    brand = "Nike"
                elif 'adidas' in name.lower():
                    brand = "Adidas"
                elif 'yeezy' in name.lower():
                    brand = "Yeezy"
                image = product_detail_json['data']['detail']['logoUrl']
                soldNum = product_detail_json['data']['detail']['soldNum']
                retail_price = int(str(product_detail_json['data']['detail']['authPrice'])[:-2])
                retail_date = product_detail_json['data']['detail']['sellDate']
                articleNumber = product_detail_json['data']['detail']['articleNumber']
                try:
                    download_image(articleNumber, image)
                    image = 'sneakers/2020/01/' + articleNumber + '.jpg'

                    parms = (
                        productId, brand, name, articleNumber, image, retail_price, retail_date, soldNum,
                        datetime.now())
                    insert_info = """
                                INSERT INTO sneakers_sneakers(`id_in_du`, `brand`, `name`, `style`, `image`,
                                `retail_price`, `retail_date`, `sold_nums`, `add_time`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                ON DUPLICATE KEY UPDATE `sold_nums`=VALUES (`sold_nums`), `add_time`=VALUES (`add_time`)
                            """
                    cursor.execute(insert_info, parms)
                    db.commit()

                    for size_price in product_detail_json['data']['sizeList']:
                        if str(size_price['item']['price'])[:-2]:
                            size = float(size_price['size'])
                            price = int(str(size_price['item']['price'])[:-2])
                            size_info.append((productId, articleNumber, size, price))
                        else:
                            size = float(size_price['size'])
                            size_info.append((productId, articleNumber, size, 0))
                    insert_price = """
                                INSERT INTO sneakers_price(`id_in_du_id`, `style`, `size`, `price`) VALUES (%s,%s,%s,%s)
                                ON DUPLICATE KEY UPDATE `price`=VALUES (`price`)
                            """
                    cursor.executemany(insert_price, size_info)
                    db.commit()

                    print(str(productId) + " " + name + " " + "Success")
                except:
                    continue


# 多线程
class MyThread(threading.Thread):
    def __init__(self, func):
        threading.Thread.__init__(self)
        self.func = func

    def run(self):
        self.func()


def main():
    id_list = [54685, 56162, 39628, 69865, 50352, 10351, 2, 1, 623, 624, 38258, 23831, 49180, 47695, 29149,
               52171, 58302, 29151, 64614, 14886, 9534, 9235, 54775, 50677, 38616, 36191, 47740, 11063, 10904,
               10459, 9306, 15693, 8714, 13883, 9145, 790, 15081, 15554, 20286, 16856, 17438, 12578, 21991,
               12366, 15082, 2205, 16211, 5878, 2423, 2204, 9951, 5330, 5704, 9708]
    threads = []
    for task in id_list:
        q.put(task)
    for i in range(threadNum):  # 开启多个线程
        thread = MyThread(get_product_detail)
        thread.start()
        print('Thread' + str(i) + '开启')
        threads.append(thread)
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    q = queue.Queue()
    threadNum = 8
    main()

# if __name__ == '__main__':
#     groups = [x for x in range(1, 72781)]
#     pool = Pool()
#     pool.map(get_product_detail, groups)

# get_product_detail(53489)
# get_recentsales_info(0, 53489)


# 商品详情接口
# product_detail_url = get_product_detail_url(72780)
# print(product_detail_url)
# product_detail_response = requests.get(url=product_detail_url, headers=headers)
# print(product_detail_response.text)

# 最近购买
# recensales_list_url = get_recensales_list_url(0, 40755)
# recensales_list_response = requests.get(url=recensales_list_url, headers=headers)
# print(recensales_list_response.text)
#
# # 关键词搜索商品
# search_by_keywords_url = get_search_by_keywords_url(0, 1, 0)
# search_by_keywords_response = requests.get(url=search_by_keywords_url, headers=headers)
# print(search_by_keywords_response.text)
#
# # 商品品类列表
# brand_list_url = get_brand_list_url(1, 4)
# brand_list_response = requests.get(url=brand_list_url, headers=headers)
# print(brand_list_response.text)
