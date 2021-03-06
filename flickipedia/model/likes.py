"""
Likes model class
"""

from flickipedia.model.base_model import BaseModel
from flickipedia.config import log, schema
from sqlalchemy.sql import func


class LikeModel(BaseModel):

    def __init__(self):
        super(LikeModel, self).__init__()

    def get_like(self, user_id, article_id, photo_id):
        """ Retrieve whether an object has been liked """
        schema_obj = getattr(schema, 'Like')
        query_obj = self.io.session.query(schema_obj).filter(
            schema_obj.user_id == user_id,
            schema_obj.article_id == article_id,
            schema_obj.photo_id == photo_id,
        )
        res = self.alchemy_fetch_validate(query_obj)
        if len(res) > 0:
            return res[0]
        else:
            return None

    def get_likes_article_photo(self, article_id, photo_id, count=False):
        """ Retrieve the full set of endorsements for a article-photo """
        schema_obj = getattr(schema, 'Like')
        res = self.io.session.query(schema_obj).filter(
            schema_obj.article_id == article_id,
            schema_obj.photo_id == photo_id,
        )
        if count:
            return res.count()
        else:
            return res.all()

    def insert_like(self, user_id, article_id, photo_id):
        return self.io.insert('Like', user_id=user_id,
                              article_id=article_id, photo_id=photo_id)

    def delete_like(self, like_obj):
        return self.io.delete(like_obj)

    def get_most_likes(self, limit):
        """ Return likes counts by photo and article"""
        schema_obj = getattr(schema, 'Like')
        query_obj = self.io.session.query(
            schema_obj.photo_id, schema_obj.article_id, func.count(
                schema_obj.photo_id).label('cnt')).group_by(
                    schema_obj.photo_id, schema_obj.article_id).order_by(
                        'cnt DESC').limit(limit)
        res = self.alchemy_fetch_validate(query_obj)
        return res

