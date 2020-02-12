import requests
import json
import time
from lxml import etree


HEARERS = {
    'x-api-key': '99WtRZK6pS1Fqt8hXBfWq8BYQjErmwipa3a0hYxX',
    'User-Agent': 'StockX/29919 CFNetwork/1121.2.2 Darwin/19.3.0',
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
}


def get_response(url):
    response = requests.get(url, headers=HEARERS)
    data = response.text
    return data

# def get_product_key(search):
#     url = 'https://stockx.com/api/browse?productCategory=sneakers&_search=' + search + '&dataType=product&country=CN'
#     data = get_response(url)
#     result_json = json.loads(data)
#     for product in result_json['Products'][:5]:
#         if product['styleId'].lower() == search.lower():
#             return product['urlKey']
#     return None
#
#
# def get_product_price(search):
#     size_list = []
#     urlKey = get_product_key(search)
#     if urlKey:
#         url = "https://stockx.com/" + urlKey
#         data = get_response(url)
#
#         html = etree.HTML(data)
#         price_info = html.xpath("//div[@class='product-content']//ul[contains(@class,'list-unstyled')]/li")
#         for li in price_info[1:]:
#             size_dict = {}
#             size = li.xpath("./div[@class='inset']/div[@class='title']/text()")[0].replace(" ", "")
#             price = li.xpath("./div[@class='inset']/div[@class='subtitle']/text()")[0].replace(",", "")
#             if price == 'Bid':
#                 price = '$0'
#             size_dict['size'] = size
#             size_dict['price'] = price
#             size_list.append(size_dict)
#         return size_list
#     else:
#         return None
#
#
# print(get_product_price('CJ5290-600'))


# 手机端爬取
def get_product_uuid(search):
    url = 'https://gateway.stockx.com/api/v3/browse?_search=' + search + '&dataType=product&order=DESC&sort=featured&currency=USD&country=US'
    # url = 'https://stockx.com/api/browse?productCategory=sneakers&_search=' + search + '&dataType=product&country=US'
    data = get_response(url)
    result_json = json.loads(data)
    for product in result_json['Products'][:5]:
        if product['styleId'].lower() == search.lower():
            return product['uuid']
    return None


def get_product_price(search):
    size_list = []
    uuid = get_product_uuid(search)
    if uuid:
        url = 'https://gateway.stockx.com/api/v2/products/' + uuid + '?includes=market,360&currency=USD&country=US'
        data = get_response(url)
        result_json = json.loads(data)
        for size_id in result_json['Product']['children']:
            size_dict = {}
            size_dict['size'] = result_json['Product']['children'][size_id]['shoeSize']
            size_dict['price'] = result_json['Product']['children'][size_id]['market']['lowestAskFloat']
            size_list.append(size_dict)
            # size_dict['US{0}'.format(result_json['Product']['children'][size_id]['shoeSize'])] = result_json['Product']['children'][size_id]['market']['lowestAskFloat']
        return size_list
    else:
        return None
