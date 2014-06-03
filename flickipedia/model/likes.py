"""
Likes model class
"""

from flickipedia.config import log, schema
from flickipedia.mysqlio import DataIOMySQL


class LikeModel(object):

    def __init__(self):
        super(LikeModel, self).__init__()

        self.io = DataIOMySQL()
        self.io.connect()

    def get_like(self, user_id, article_id, photo_id):
        """ Retrieve whether an object has been liked """
        schema_obj = getattr(schema, 'Like')
        res = self.io.session.query(schema_obj).filter(
            schema_obj.user_id == user_id,
            schema_obj.article_id == article_id,
            schema_obj.photo_id == photo_id,
        ).all()
        if len(res) > 0:
            return res[0]
        else:
            return None

    def get_likes_article_photo(self, article_id, photo_id):
        """ Retrieve the full set of endorsements for a article-photo """
        schema_obj = getattr(schema, 'Like')
        res = self.io.session.query(schema_obj).filter(
            schema_obj.article_id == article_id,
            schema_obj.photo_id == photo_id,
        ).all()
        return res

    def insert_like(self, user_id, article_id, photo_id):
        return self.io.insert('Like', user_id=user_id,
                              article_id=article_id, photo_id=photo_id)

    def delete_like(self, like_obj):
        return self.io.delete(like_obj)