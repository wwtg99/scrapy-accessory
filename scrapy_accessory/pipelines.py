from scrapy.utils.serialize import ScrapyJSONEncoder
from scrapy.exceptions import NotConfigured


class RedisListPipeline:

    DEFAULT_QUEUE = 'queue'
    DEFAULT_MAX_RETRY = 5

    serializer = ScrapyJSONEncoder().encode

    def __init__(self, conn_url: str, queue: str, max_retry=None):
        try:
            import redis
        except ImportError:
            raise NotConfigured('missing redis library')
        self._conn = redis.from_url(conn_url)
        self.queue = queue or self.DEFAULT_QUEUE
        self.max_retry = max_retry or self.DEFAULT_MAX_RETRY

    @classmethod
    def from_crawler(cls, crawler):
        if hasattr(crawler.spider, 'queue'):
            queue = crawler.spider.queue
        else:
            queue = crawler.settings.get('REDIS_DEFAULT_QUEUE')
        return cls(
            conn_url=crawler.settings.get('REDIS_CONNECTION_URL'),
            queue=queue,
            max_retry=crawler.settings.get('REDIS_MAX_RETRY')
        )

    def process_item(self, item, spider):
        data = self.serializer(item)
        try_time = 0
        while try_time < self.max_retry:
            try:
                self._conn.rpush(self.queue, data)
                return item
            except Exception:
                spider.logger.error('process item failed {}'.format(item))
                try_time += 1
        spider.logger.error('Give up item for failed {} times {}'.format(try_time, item))
        return item

    def close(self):
        self._conn.close()
