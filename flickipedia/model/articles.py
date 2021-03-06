"""
Article model class
"""

import time

from flickipedia.model.base_model import BaseModel
from flickipedia.config import log, schema
from sqlalchemy.sql import func


class ArticleContentModel(BaseModel):

    def __init__(self):
        super(ArticleContentModel, self).__init__()

    def get_article_content(self, aid):
        """Fetch Article Content
        :param article: str, article name
        :return:        Article schema object or None
        """
        schema_obj = getattr(schema, 'ArticleContent')
        query_obj = self.io.session.query(schema_obj).filter(
            schema_obj.aid == aid)
        res = self.alchemy_fetch_validate(query_obj)
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


class ArticleModel(BaseModel):

    def __init__(self):
        super(ArticleModel, self).__init__()

    def get_max_id(self):
        """
        Fetch maximum article id
        :return: int id
        """
        schema_obj = getattr(schema, 'Article')
        query_obj = self.io.session.query(func.max(schema_obj._id).label('id'))
        res = self.alchemy_fetch_validate(query_obj)
        if len(res) > 0:
            return res[0].id
        else:
            log.error('Couldn\'t get max article id.')
            return 0


    def get_article_count(self):
        """ Fetches the number of articles indexed in the DB
        :return: Integer value of article count
        """
        schema_obj = getattr(schema, 'Article')
        query_obj = self.io.session.query(func.count(
                schema_obj._id).label('cnt'))
        res = self.alchemy_fetch_validate(query_obj)
        if len(res) > 0:
            return res[0].cnt
        else:
            log.error('Couldn\'t get the count of articles.')
            return 0

    def get_article_by_name(self, article):
        """Fetch Article
        :param article: str, article name
        :return:        Article schema object or None
        """
        schema_obj = getattr(schema, 'Article')
        query_obj = self.io.session.query(schema_obj).filter(
            schema_obj.article_name == article)
        res = self.alchemy_fetch_validate(query_obj)
        if len(res) > 0:
            return res[0]
        else:
            return None

    def get_article_by_id(self, id):
        """Fetch Article
        :param id:      str, article id
        :return:        Article schema object or None
        """
        schema_obj = getattr(schema, 'Article')
        query_obj = self.io.session.query(schema_obj).filter(
            schema_obj._id == id)
        res = self.alchemy_fetch_validate(query_obj)
        if len(res) > 0:
            return res[0]
        else:
            return None

    def insert_article(self, article, pageid, id=None):
        if id:
            return self.io.insert('Article', wiki_aid=pageid,
                article_name=article, last_access=int(time.time()))
        else:
            return self.io.insert('Article', _id=id, wiki_aid=pageid,
                article_name=article, last_access=int(time.time()))

    def delete_article(self, id):
        self.io.session.delete(self.get_article_by_id(id))
        self.io.session.commit()

    def get_most_recently_accessed(self, limit):
        """Retrieve most recently accessed articles"""
        schema_obj = getattr(schema, 'Article')
        query_obj = self.io.session.query(schema_obj).order_by(
            schema_obj.last_access.desc()).limit(limit)
        res = self.alchemy_fetch_validate(query_obj)
        return res

    def update_last_access(self, _id):
        """Update the last access time"""
        schema_obj = getattr(schema, 'Article')
        self.io.session.query(schema_obj).filter(schema_obj._id == _id).update(
                {schema_obj.last_access: int(time.time())})
        self.io.session.commit()
