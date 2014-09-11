"""
User model class
"""

from flickipedia.model.base_model import BaseModel, RET_TYPE_FIRSTROW
from flickipedia.config import log, schema


class UserModel(BaseModel):

    def __init__(self):
        super(UserModel, self).__init__()

    def fetch_user_by_id(self, uid):
        query_obj = self.io.session.query(schema.User).filter(
            schema.User._id == uid)
        try:
            return self.alchemy_fetch_validate(query_obj, RET_TYPE_FIRSTROW)
        except (KeyError, IndexError) as e:
            log.info('User not found "%s": %s' % (uid, e.message))
            return None

    def fetch_user_by_name(self, handle):
        query_obj = self.io.session.query(schema.User).filter(
            schema.User.handle == handle)
        try:
            return self.alchemy_fetch_validate(query_obj, RET_TYPE_FIRSTROW)
        except (KeyError, IndexError) as e:
            log.info('User not found "%s": %s' % (handle, e.message))
            return None
