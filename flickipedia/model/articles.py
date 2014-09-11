"""
Article model class
"""

import time

from flickipedia.config import log, schema
from flickipedia.mysqlio import DataIOMySQL
from MySQLdb import OperationalError


NUM_SQL_RETRIES = 5


class ArticleContentModel(object):

    def __init__(self):
        super(ArticleContentModel, self).__init__()
        self.io = DataIOMySQL()
        self.io.connect()

    def get_article_content(self, aid):
        """Fetch Article Content
        :param article: str, article name
        :return:        Article schema object or None
        """
        schema_obj = getattr(schema, 'ArticleContent')
        res = self.io.session.query(schema_obj).filter(
            schema_obj.aid == aid).all()
        if len(res) > 0:
            return res[0]
        else:
            return None

    def insert_article(self, aid, markup):
        return self.io.insert('ArticleContent', aid=aid, markup=markup)

    def update_article(self, aid, markup):
        """Update the last access time"""
        schema_obj = getattr(schema, 'ArticleContent')
        self.io.session.query(schema_obj).filter(schema_obj.aid == aid).update(
                {schema_obj.markup: markup})
        self.io.session.commit()


class ArticleModel(object):

    def __init__(self):
        super(ArticleModel, self).__init__()
        self.io = DataIOMySQL()
        self.io.connect()

    def get_article_by_name(self, article):
        """Fetch Article
        :param article: str, article name
        :return:        Article schema object or None
        """
        retries = 0
        res = []
        schema_obj = getattr(schema, 'Article')
        while retries < NUM_SQL_RETRIES:
            try:
                res = self.io.session.query(schema_obj).filter(
                    schema_obj.article_name == article).all()
                break
            except OperationalError:
                log.error('Failed to fetch article, trying again.')
                retries += 1
                time.sleep(0.5)

        if len(res) > 0:
            return res[0]
        else:
            return None

    def insert_article(self, article, pageid):
        return self.io.insert('Article', wiki_aid=pageid,
            article_name=article, last_access=int(time.time()))

    def get_most_recently_accessed(self, limit):
        """Retrieve most recently accessed articles"""
        schema_obj = getattr(schema, 'Article')
        return self.io.session.query(schema_obj).order_by(
            schema_obj.last_access.desc()).limit(limit).all()

    def update_last_access(self, _id):
        """Update the last access time"""
        schema_obj = getattr(schema, 'Article')
        self.io.session.query(schema_obj).filter(schema_obj._id == _id).update(
                {schema_obj.last_access: int(time.time())})
        self.io.session.commit()
