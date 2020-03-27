Scrapy Accessory
================

# Introduction

Useful accessory utilities for [Scrapy](https://scrapy.org/).

Containing:

- middleware
- feed exporter storage backend

# Installation

```
pip install scrapy-accessory
```

# Usage

## Middleware

### RandomUserAgentDownloadMiddleware

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

### ProxyDownloadMiddleware

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

## Feed exporter storage backend

### ObsFeedStorage

Feed exporter storage backend for huawei cloud OBS.

Install obs sdk first

```
pip install esdk-obs-python
```

Configure in settings.py

```python
FEED_STORAGES = {
    'obs': 'scrapy_accessory.feedexporter.ObsFeedStorage',
}
HUAWEI_ACCESS_KEY_ID = '<your access key id>'
HUAWEI_SECRET_ACCESS_KEY = '<your secret access key>'
HUAWEI_OBS_ENDPOINT = '<your obs bucket endpoint> ex: https://obs.cn-north-4.myhuaweicloud.com'
```

Output to OBS by obs schema `-o obs://<bucket>/<key>`

### OssFeedStorage

Feed exporter storage backend for ali cloud OSS.

Install oss sdk first

```
pip install oss2
```

Configure in settings.py

```python
FEED_STORAGES = {
    'oss': 'scrapy_accessory.feedexporter.OssFeedStorage',
}
ALI_ACCESS_KEY_ID = '<your access key id>'
ALI_SECRET_ACCESS_KEY = '<your secret access key>'
ALI_OSS_ENDPOINT = '<your oss bucket endpoint> ex: https://oss-cn-beijing.aliyuncs.com'
```

Output to OSS by oss schema `-o oss://<bucket>/<key>`
