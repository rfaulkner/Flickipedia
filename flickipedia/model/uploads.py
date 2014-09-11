"""
Photo model class
"""

from flickipedia.model.base_model import BaseModel
from flickipedia.config import log, schema
from flickipedia.mysqlio import DataIOMySQL


class UploadsModel(BaseModel):

    def __init__(self):
        super(UploadsModel, self).__init__()
        self.io = DataIOMySQL()
        self.io.connect()

    def get_upload(self, flickr_photo_id):
        """
        Retrieve a photo by its flickr id
        """
        log.info('Fetching photo by flickr_photo_id: %s' % flickr_photo_id)
        schema_obj = getattr(schema, 'Upload')
        query_obj = self.io.session.query(schema_obj).filter(
            schema_obj.flickr_photo_id == flickr_photo_id)
        res = self.alchemy_fetch_validate(query_obj)
        if len(res) > 0:
            return res[0]
        else:
            return None

    def insert_upload(self, photo_id, flickr_photo_id, article_id, user_id):
        return self.io.insert('Upload',
                              photo_id=photo_id,
                              flickr_photo_id=flickr_photo_id,
                              article_id=article_id,
                              user_id=user_id,
        )
