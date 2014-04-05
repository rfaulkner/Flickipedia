"""
Handle MySQL I/O via sqlalchemy engine and ORM
"""

import MySQLdb as mysql

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flickipedia import schema

from flickipedia.config import log


class DataIOMySQL(object):
    """ Class implementing data IO for MySQL. Utilizes sqlalchemy [1].

    Database and table schemas will be stored in versus/schema.  Modifications
    to this schema will be persisted with sync

    [1] http://docs.sqlalchemy.org
    """

    DEFAULTS = {
        'dialect': 'mysql',
        'driver': '',
        'host': 'localhost',
        'port': 3306,
        'db': 'test',
        'user': 'root',
        'pwrd': '',
    }

    def __init__(self, **kwargs):
        super(DataIOMySQL, self).__init__(**kwargs)

        self.engine = None
        self.sess = None

        for key in self.DEFAULTS.keys():
            if kwargs.has_key(key):
                setattr(self, key, kwargs[key])
            else:
                setattr(self, key, self.DEFAULTS[key])

    def connect(self, **kwargs):
        """ dialect+driver://username:password@host:port/database """
        if self.driver:
            connect_str = '{0}+{1}://{2}:{3}@{4}/{5}'.format(
                self.dialect,
                self.driver,
                self.user,
                self.pwrd,
                self.host,
                self.db,
            )
        else:
            connect_str = '{0}://{1}:{2}@{3}/{4}'.format(
                self.dialect,
                self.user,
                self.pwrd,
                self.host,
                self.db,
            )
        log.info('Establishing connection to "%s"' % connect_str)
        self.engine = create_engine(connect_str)
        self.make_session()

    def connect_lite(self):
        """ Use an in-memory db """
        self.engine = create_engine('sqlite://')
        self.make_session()

    def make_session(self):
        """ Create a session """
        Session = sessionmaker()
        Session.configure(bind=self.engine)
        self.sess = Session()

    @property
    def session(self):
        return self.sess

    def create_table(self, obj_name):
        """
        Method for table creation

        :param name:    schema object name

        :return:        boolean indicating status
        """
        if hasattr(schema, obj_name):
            getattr(schema, obj_name).__table__.create(bind=self.engine)
            return True
        else:
            log.error('Schema object not found for "%s"' % obj_name)
            return False

    def fetch_all_rows(self, obj_name):
        """
        Method to extract all rows from database.

        :param name:    object to persist

        :return:        row list from table
        """
        obj = getattr(schema, obj_name)
        return self.session.query(obj, obj.name).all()

    def insert(self, obj_name, **kwargs):
        """
        Method to insert rows in database

        :param name:        object to persist
        :param **kwargs:    field values

        :return:    boolean indicating status of action
        """
        if not self.session:
            log.error('No session')
            return False
        try:
            self.session.add(getattr(schema, obj_name)(**kwargs))
            self.session.commit()
            return True
        except Exception as e:
            log.error('Failed to insert row: "%s"' % e.message)
            return False

    def delete(self, qry_obj):
        """
        Method to delete rows from database

        :param qry_obj:        object to delete

        :return:    boolean indicating status of action
        """
        if not self.session:
            log.error('No session')
            return False
        try:
            self.session.delete(qry_obj)
            self.session.commit()
            return True
        except Exception as e:
            log.error('Failed to delete row "%s": "%s"' % (str(qry_obj), e.message()))
            return False
