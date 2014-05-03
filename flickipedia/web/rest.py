"""
Defines restful interface to backend

"""

from flickipedia.mysqlio import DataIOMySQL
from flickipedia.config import schema


def set_glyph(user, photo_id, article_id):
    """ Toggles the like-glyph value for the given triplet """

    io = DataIOMySQL()
    io.connect()

    curr = get_glyph(user, photo_id, article_id)

    # toggle and set new value (delete row if it doesn't exist)
    if curr:
        # io.update false
        pass
    else:
        # io.update true
        pass

    # get glyph current state

    raise NotImplementedError()
    # return

def get_glyph(user, photo_id, article_id):
    """ Determines the like-glyph value for the given triplet """
    io = DataIOMySQL()
    io.connect()

    schema_obj = getattr(schema, 'Likes')
    return io.session.query(schema_obj, schema_obj.is_set).filter(
        schema_obj.photo_id == photo_id,
        schema_obj.article_id == article_id,
        schema_obj.user_id == user
    )[0]

