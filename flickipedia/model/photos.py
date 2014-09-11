"""
Photo model class
"""

from flickipedia.model.base_model import BaseModel
from flickipedia.config import log, schema


class PhotoModel(BaseModel):

    def __init__(self):
        super(PhotoModel, self).__init__()

    def get_photo(self, flickr_id, article_id):
        """
        Retrieve a photo by its flickr id
        """
        log.info('Fetching photo by flickr ID: %s' % flickr_id)
        schema_obj = getattr(schema, 'Photo')
        query_obj = self.io.session.query(schema_obj).filter(
            schema_obj.flickr_id == flickr_id,
            schema_obj.article_id == article_id)
        res = self.alchemy_fetch_validate(query_obj)
        if len(res) > 0:
            return res[0]
        else:
            return None

    def insert_photo(self, flickr_id, article_id):
        return self.io.insert('Photo', flickr_id=flickr_id,
                              article_id=article_id, votes=0)
