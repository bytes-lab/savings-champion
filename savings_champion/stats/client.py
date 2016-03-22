__author__ = 'josh'
import statsd
from django.conf import settings


class StatsDClient(object):
    def __init__(self):
        self.connection = statsd.Connection(host=settings.STATSD_HOST,
                                            port=settings.STATSD_PORT,
                                            sample_rate=settings.STATSD_SAMPLE_RATE,
                                            disabled=False)

    def get_counter_client(self, client_name):
        return statsd.Client(settings.STATSD_BASE_CLIENT_NAME, self.connection).get_client(name=client_name,
                                                                                           class_=statsd.Counter)

    def get_timer_client(self, client_name):
        return statsd.Client(settings.STATSD_BASE_CLIENT_NAME, self.connection).get_client(name=client_name,
                                                                                           class_=statsd.Timer)

    def get_gauge_client(self, client_name):
        return statsd.Client(settings.STATSD_BASE_CLIENT_NAME, self.connection).get_client(name=client_name,
                                                                                           class_=statsd.Gauge)

    def get_average_client(self, client_name):
        return statsd.Client(settings.STATSD_BASE_CLIENT_NAME, self.connection).get_client(name=client_name,
                                                                                           class_=statsd.Average)

    def get_raw_client(self, client_name):
        return statsd.Client(settings.STATSD_BASE_CLIENT_NAME, self.connection).get_client(name=client_name,
                                                                                           class_=statsd.Raw)
