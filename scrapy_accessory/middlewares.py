import random
import time
import logging
from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware


class RandomUserAgentDownloadMiddleware(UserAgentMiddleware):
    """
    A download middleware for generate random user-agent header for request.

    Configurations in the settings:

    USER_AGENT_LIST_FILE: path to user-agent file, one user-agent per line.
    USER_AGENT_LIST: a list or tuple of user-agent to use.

    The middleware will use USER_AGENT_LIST_FILE if provided,
    otherwise use USER_AGENT_LIST if provided,
    finally use USER_AGENT or whatever was passed to the middleware.
    """
    def __init__(self, settings, user_agent='Scrapy'):
        super().__init__()
        self.user_agent = user_agent
        user_agent_list_file = settings.get('USER_AGENT_LIST_FILE')
        user_agent_list = settings.get('USER_AGENT_LIST')
        if user_agent_list_file:
            with open(user_agent_list_file, 'r') as f:
                self.user_agent_list = [line.strip() for line in f.readlines()]
        elif user_agent_list and isinstance(user_agent_list, (list, tuple)):
            self.user_agent_list = user_agent_list
        else:
            self.user_agent_list = [settings.get('USER_AGENT', user_agent)]

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.settings)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agent_list)
        if user_agent:
            request.headers.setdefault('User-Agent', user_agent)


class ProxyDownloadMiddleware(object):
    """
    A download middleware for configure proxy for request.
    This middleware use static proxy by default, if want to use dynamic proxy, extend the class and implement the
    generate_proxy method.

    Configurations in the settings:

    PROXY_ENABLED: True to use proxy, default is False
    PROXY_HOST: default static proxy, format: <ip>:<port>, default empty
    PROXY_CACHE: cache for proxy, use redis://<host>:<port>/<db> to use redis cache, default dict in memory
    PROXY_TTL: proxy cache ttl in seconds, default 30s
    CHANGE_PROXY_STATUS: a list of status codes that force to change proxy if received, default [429]

    An example to generate dynamic proxy:
    ```
    def generate_proxy(self):
        res = requests.get(api)  # generate from remote proxy api
        if res.status_code < 300:
            return res.text  # return proxy type <ip>:<port>
        return None
    ```
    """
    PROXY_KEY = 'SCRAPY_PROXY'
    DEFAULT_PROXY_TTL = 0  # default proxy ttl, 0 for no expiration
    DEFAULT_CHANGE_PROXY_STATUS = [429]

    def __init__(self, settings):
        super().__init__()
        self.enabled = settings.get('PROXY_ENABLED') or False
        self.proxy = settings.get('PROXY_HOST')
        cache = settings.get('PROXY_CACHE')
        self.proxy_ttl = settings.get('PROXY_TTL') or self.DEFAULT_PROXY_TTL
        self.change_proxy_status = settings.get('CHANGE_PROXY_STATUS') or self.DEFAULT_CHANGE_PROXY_STATUS
        if cache:
            if cache.startswith('redis://'):
                import redis
                self.cache_type = 'redis'
                self.cache = redis.Redis.from_url(cache)
        else:
            self.cache_type = 'dict'
            self.cache = dict()

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.settings)
        return o

    def process_request(self, request, spider):
        proxy = self.get_proxy()
        if proxy:
            if request.url.startswith("http://"):
                request.meta['proxy'] = 'http://' + proxy
            elif request.url.startswith("https://"):
                request.meta['proxy'] = "https://" + proxy

    def process_response(self, request, response, spider):
        if "proxy" in request.meta.keys():
            logging.debug('Get () with response code {} by proxy {}'.format(
                request.url, response.status, request.meta['proxy']))
        if response.status in self.change_proxy_status:
            self.get_proxy(force_new=True)
            new_request = request.copy()
            new_request.dont_filter = True
            return new_request
        else:
            return response

    def get_proxy(self, force_new=False):
        if not self.enabled:
            return None
        # check cache exists
        if not force_new:
            proxy = self.get_from_cache()
            if proxy:
                return proxy
        # if force new or no cache hit
        proxy = self.generate_proxy()
        if proxy:
            self.set_to_cache(proxy)
        return proxy

    def get_from_cache(self):
        if self.cache_type == 'redis':
            proxy = self.cache.get(self.PROXY_KEY)
            if proxy:
                return proxy.decode()
        elif self.cache_type == 'dict':
            data = self.cache.get(self.PROXY_KEY)
            if data:
                expire = data['expire']
                if expire > time.time():
                    return data['value']
                else:
                    del self.cache[self.PROXY_KEY]
        return None

    def set_to_cache(self, proxy):
        if self.cache_type == 'redis':
            self.cache.set(self.PROXY_KEY, proxy, self.proxy_ttl)
        elif self.cache_type == 'dict':
            self.cache[self.PROXY_KEY] = {'value': proxy, 'expire': time.time() + self.proxy_ttl}

    def generate_proxy(self):
        return self.proxy
