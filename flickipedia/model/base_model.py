"""
Provides a base module for defining generic modeling logic
"""

import time
from MySQLdb import OperationalError
from flickipedia.config import log, schema

NUM_SQL_RETRIES = 5


class BaseModel(object):
    """
    Base class for model objects that can handle generic validation and state
     logic
    """

    def alchemy_fetch_validate(self, sqlAlchemyQryObj):
        """
        Fault tolerance around query execution in sql alachemy
        :param schema_obj:
        :return:
        """
        retries = 0
        while retries < NUM_SQL_RETRIES:
            try:
                return sqlAlchemyQryObj.all()
            except OperationalError:
                log.error('Failed to fetch article, trying again.')
                retries += 1
                time.sleep(0.5)
        return []