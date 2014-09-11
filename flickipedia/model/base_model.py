"""
Provides a base module for defining generic modeling logic
"""

import time
from MySQLdb import OperationalError
from flickipedia.config import log, schema
from flickipedia.mysqlio import DataIOMySQL

NUM_SQL_RETRIES = 5

RET_TYPE_ALLROWS = 'allrows'
RET_TYPE_COUNT = 'count'
RET_TYPE_FIRSTROW = 'firstrow'


class BaseModel(object):
    """
        Base class for model objects that can handle generic validation and state
        logic
    """

    def __init__(self):
        super(BaseModel, self).__init__()
        self.io = DataIOMySQL()
        self.io.connect()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.io.sess.close()
        self.io.engine.dispose()

    def alchemy_fetch_validate(self, sqlAlchemyQryObj, retType = RET_TYPE_ALLROWS):
        """
        Fault tolerance around query execution in sql alachemy
        :param schema_obj:
        :return:
        """
        retries = 0
        while retries < NUM_SQL_RETRIES:
            try:
                if retType == RET_TYPE_ALLROWS:
                    return sqlAlchemyQryObj.all()
                elif retType == RET_TYPE_COUNT:
                    return sqlAlchemyQryObj.count()
                elif retType == RET_TYPE_FIRSTROW:
                    return sqlAlchemyQryObj[0]
            except OperationalError:
                log.error('Failed to fetch article, trying again.')
                retries += 1
                time.sleep(0.5)
        return []