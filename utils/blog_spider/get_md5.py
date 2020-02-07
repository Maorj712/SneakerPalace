import hashlib


def get_md5(url):
    m = hashlib.md5()
    value = url.encode(encoding='utf-8')
    m.update(value)
    url_md5 = m.hexdigest()
    return url_md5
