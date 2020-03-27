from urllib.parse import urlparse
from scrapy.extensions.feedexport import BlockingFeedStorage
from scrapy.exceptions import NotConfigured


class ObsFeedStorage(BlockingFeedStorage):
    """
    Feed exporter storage backend for huawei cloud OBS.
    """

    def __init__(self, uri, access_key=None, secret_key=None, endpoint=None):
        u = urlparse(uri)
        self.bucketname = u.hostname
        self.access_key = u.username or access_key
        self.secret_key = u.password or secret_key
        self.endpoint = endpoint

        self.keyname = u.path[1:]  # remove first "/"
        if access_key is None or secret_key is None or endpoint is None:
            raise NotConfigured('missing access_key or secret_key or endpoint for huawei cloud')
        try:
            from obs import ObsClient
        except ImportError:
            raise NotConfigured('missing esdk-obs-python library')
        self.obs_client = ObsClient(
            access_key_id=self.access_key,
            secret_access_key=self.secret_key,
            server=self.endpoint
        )

    @classmethod
    def from_crawler(cls, crawler, uri):
        return cls(
            uri=uri,
            access_key=crawler.settings['HUAWEI_ACCESS_KEY_ID'],
            secret_key=crawler.settings['HUAWEI_SECRET_ACCESS_KEY'],
            endpoint=crawler.settings['HUAWEI_OBS_ENDPOINT'],
        )

    @classmethod
    def from_settings(cls, settings, uri):
        return cls(
            uri=uri,
            access_key=settings['HUAWEI_ACCESS_KEY_ID'],
            secret_key=settings['HUAWEI_SECRET_ACCESS_KEY'],
            endpoint=settings['HUAWEI_OBS_ENDPOINT'],
        )

    def _store_in_thread(self, file):
        file.seek(0)
        resp = self.obs_client.putContent(self.bucketname, self.keyname, file)
        if resp.status >= 300:
            raise IOError('{}: {}'.format(resp.errorCode, resp.errorMessage))


class OssFeedStorage(BlockingFeedStorage):
    """
    Feed exporter storage backend for ali cloud OSS.
    """

    def __init__(self, uri, access_key=None, secret_key=None, endpoint=None):
        u = urlparse(uri)
        self.bucketname = u.hostname
        self.access_key = u.username or access_key
        self.secret_key = u.password or secret_key
        self.endpoint = endpoint

        self.keyname = u.path[1:]  # remove first "/"
        if access_key is None or secret_key is None or endpoint is None:
            raise NotConfigured('missing access_key or secret_key or endpoint for ali cloud')
        try:
            import oss2
        except ImportError:
            raise NotConfigured('missing oss2 library')
        auth = oss2.Auth(self.access_key, self.secret_key)
        self.oss_client = oss2.Bucket(auth, self.endpoint, self.bucketname)

    @classmethod
    def from_crawler(cls, crawler, uri):
        return cls(
            uri=uri,
            access_key=crawler.settings['ALI_ACCESS_KEY_ID'],
            secret_key=crawler.settings['ALI_SECRET_ACCESS_KEY'],
            endpoint=crawler.settings['ALI_OSS_ENDPOINT'],
        )

    @classmethod
    def from_settings(cls, settings, uri):
        return cls(
            uri=uri,
            access_key=settings['ALI_ACCESS_KEY_ID'],
            secret_key=settings['ALI_SECRET_ACCESS_KEY'],
            endpoint=settings['ALI_OSS_ENDPOINT'],
        )

    def _store_in_thread(self, file):
        file.seek(0)
        resp = self.oss_client.put_object(self.keyname, file)
        if resp.status >= 300:
            raise IOError('{}: {}'.format(resp.errorCode, resp.errorMessage))
