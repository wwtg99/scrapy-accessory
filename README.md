Scrapy Accessory
================

# Installation

```
pip install scrapy-accessory
```

# Usage

## RandomUserAgentDownloadMiddleware

Add random user-agent to requests.

In settings.py add

```
# USER_AGENT_LIST_FILE = 'path-to-files'
USER_AGENT_LIST = [
    'Mozilla/5.0(compatible;MSIE9.0;WindowsNT6.1;Trident/5.0',
    'Mozilla/5.0(WindowsNT6.1;rv:2.0.1)Gecko/20100101Firefox/4.0.1',
]

DOWNLOADER_MIDDLEWARES = {
    'scrapy_accessory.middlewares.RandomUserAgentDownloadMiddleware': 200,
}
```

You can use either `USER_AGENT_LIST_FILE` or `USER_AGENT_LIST` to configure user-agents.
`USER_AGENT_LIST_FILE` points to a text file containing one user-agent per line.
`USER_AGENT_LIST` is a list or tuple of user-agents.

## ProxyDownloadMiddleware

Add http or https proxy for requests.

In settings.py add

```
PROXY_ENABLED = True  # True to use proxy, default is False
# PROXY_HOST = 'localhost:8080'  # default static proxy, format: <ip>:<port>, default empty
PROXY_CACHE = 'redis://localhost:6379/0'  # cache for proxy, use redis://<host>:<port>/<db> to use redis cache, default dict in memory
PROXY_TTL = 30 # proxy cache ttl in seconds, default 30s
CHANGE_PROXY_STATUS = [429]  # a list of status codes that force to change proxy if received, default [429]
```

Default is a static proxy configured in settings.py, you can add dynamic proxy from API or others.
Just need to extend the `ProxyDownloadMiddleware` class and implement the `generate_proxy` method.

Example:

```
class DynamicProxyDownloadMiddleware(ProxyDownloadMiddleware):

    api = 'http://api-to-get-proxy-ip'

    def generate_proxy(self):
        res = requests.get(self.api)
        if res.status_code < 300:
            return res.text  # return format <ip>:<port>
        return None
```
