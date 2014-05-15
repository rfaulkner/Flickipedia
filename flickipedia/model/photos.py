"""
Photo model class
"""

from flickipedia.config import log, schema
from flickipedia.mysqlio import DataIOMySQL


class PhotoModel(object):

    def __init__(self):
        super(PhotoModel, self).__init__()

        self.io = DataIOMySQL()
        self.io.connect()

    def get_photo_by_flickr_id(self, flickr_id):
        """
        Retrieve
        """
        schema_obj = getattr(schema, 'Photo')
        res = self.io.session.query(schema_obj).filter(
            schema_obj.flickr_id == flickr_id).all()
        if len(res) > 0:
            return res[0]
        else:
            return None

    def insert_photo(self, flickr_id, article_id):
        return self.io.insert('Photo', flickr_id=flickr_id,
                              article_id=article_id, votes=0)