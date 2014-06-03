"""
Exclude model class
"""

from flickipedia.config import log, schema
from flickipedia.mysqlio import DataIOMySQL


class ExcludeModel(object):

    def __init__(self):
        super(ExcludeModel, self).__init__()

        self.io = DataIOMySQL()
        self.io.connect()

    def get_exclude(self, user_id, article_id, photo_id):
        """ Retrieve whether an object has been voted exclude """
        schema_obj = getattr(schema, 'Exclude')
        res = self.io.session.query(schema_obj).filter(
            schema_obj.user_id == user_id,
            schema_obj.article_id == article_id,
            schema_obj.photo_id == photo_id,
        ).all()
        if len(res) > 0:
            return res[0]
        else:
            return None

    def get_excludes_article_photo(self, article_id, photo_id):
        """ Retrieve the full set of exclusions for a article-photo """
        schema_obj = getattr(schema, 'Exclude')
        res = self.io.session.query(schema_obj).filter(
            schema_obj.article_id == article_id,
            schema_obj.photo_id == photo_id,
        ).all()
        return res

    def insert_like(self, user_id, article_id, photo_id):
        return self.io.insert('Exclude', user_id=user_id,
                              article_id=article_id, photo_id=photo_id)

    def delete_like(self, like_obj):
        return self.io.delete(like_obj)