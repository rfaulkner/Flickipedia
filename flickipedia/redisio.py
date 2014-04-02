"""
Module for handling redis IO
"""

import redis
from flickipedia.config import log

__author__ = 'Ryan Faulkner'
__date__ = "2014-04-01"


class DataIORedis(object):
    """ Class implementing data IO for Redis. """

    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 6379
    DEFAULT_DB = 0

    def __init__(self, **kwargs):
        super(DataIORedis, self).__init__(**kwargs)

        self.conn = None

        self.host = kwargs['host'] if kwargs.has_key('host') else \
            self.DEFAULT_HOST
        self.port = kwargs['port'] if kwargs.has_key('port') else \
            self.DEFAULT_PORT
        self.db = kwargs['db'] if kwargs.has_key('db') else self.DEFAULT_DB

    def connect(self, **kwargs):
        self.conn = redis.Redis(host=self.host, port=self.port, db=self.db)

    def write(self, **kwargs):
        if self.conn:
            try:
                return self.conn.set(kwargs['key'], kwargs['value'])
            except KeyError as e:
                log.error('Missing param -> {0}'.format(e.message))
                return False
        else:
            log.error('No redis connection.')
            return False

    def read(self, **kwargs):
        if self.conn:
            try:
                return self.conn.get(kwargs['key'])
            except KeyError as e:
                log.error('Missing param -> {0}'.format(e.message))
                return False
        else:
            log.error('No redis connection.')
            return False

    def _del(self, **kwargs):
        if self.conn:
            try:
                return self.conn.delete(kwargs['key'])
            except KeyError as e:
                log.error('Missing param -> {0}'.format(e.message))
                return False
        else:
            log.error('No redis connection.')
            return False
