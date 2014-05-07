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
        """
        Retrieve
        """
        schema_obj = getattr(schema, 'Photo')
        res = self.io.session.query(schema_obj).filter(
            schema_obj.user_id == user_id,
            schema_obj.article_id == article_id,
            schema_obj.photo_id == photo_id,
        ).all()
        if len(res) > 0:
            return res[0]
        else:
            return None

    def insert_like(self, user_id, article_id, photo_id):
        return self.io.insert('Photo', user_id=user_id,
                              article_id=article_id, photo_id=photo_id)
