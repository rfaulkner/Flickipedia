"""
User model class
"""

from flickipedia.config import log, schema
from flickipedia.mysqlio import DataIOMySQL


class UserModel(BaseModel):

    def __init__(self):
        super(UserModel, self).__init__()

        self.io = DataIOMySQL()
        self.io.connect()
