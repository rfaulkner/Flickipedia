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

    def get_photo(self, flickr_id, article_id):
        """
        Retrieve a photo by its flickr id
        """
        log.info('Fetching photo by flickr ID: %s' % flickr_id)
        schema_obj = getattr(schema, 'Photo')
        res = self.io.session.query(schema_obj).filter(
            schema_obj.flickr_id == flickr_id,
            schema_obj.article_id == article_id).all()
        if len(res) > 0:
            return res[0]
        else:
            return None

    def insert_photo(self, flickr_id, article_id):
        return self.io.insert('Photo', flickr_id=flickr_id,
                              article_id=article_id, votes=0)
