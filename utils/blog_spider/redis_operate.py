import redis


class RedisOperate(object):

    def __init__(self):
        self.name = 'md5_url'
        if not hasattr(RedisOperate, 'pool'):
            RedisOperate.getRedisConn()
        self.conn = redis.Redis(connection_pool=RedisOperate.pool)

    @staticmethod
    def getRedisConn():
        RedisOperate.pool = redis.ConnectionPool(host='localhost', port=6379, password='pwd', db=0)

    def put(self, md5_url):
        self.conn.sadd(self.name, md5_url)

    def duplicate_checking(self, md5_url):
        result = self.conn.sismember(self.name, md5_url)
        return result
