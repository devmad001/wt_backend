import redis

class MemStorage:
    def __init__(self, host='localhost', port=6379, db=0):
        self.r = redis.Redis(host=host, port=port, db=db)

    def set_value(self, key, value):
        self.r.set(key, value)

    def get_value(self, key):
        return self.r.get(key)

    def delete_value(self, key):
        self.r.delete(key)
