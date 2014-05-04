"""
Defines restful interface to backend

"""

from flickipedia.mysqlio import DataIOMySQL
from flickipedia.config import schema
from flickipedia.config import log


def api_set_glyph(user, photo_id, article_id):
    """ Toggles the like-glyph value for the given triplet """

    io = DataIOMySQL()
    io.connect()

    result = api_get_glyph(user, photo_id, article_id)

    # toggle and set new value (delete row if it doesn't exist)
    if result:
        # io.update false
        pass
    else:
        # io.update true
        pass


    raise NotImplementedError()
    # return

def api_get_glyph(uid, pid, aid):
    """ Determines the like-glyph value for the given triplet """
    io = DataIOMySQL()
    io.connect()
    schema_obj = getattr(schema, 'Likes')

    # Query to extract
    res = io.session.query(schema_obj, schema_obj.is_set).filter(
        schema_obj.photo_id == pid,
        schema_obj.article_id == aid,
        schema_obj.user_id == uid
    ).limit(1).all()

    if len(res) == 0:
        log.error('REST \'api_get_glyph\': Couldn\'t find ('
                  'user="%s", photo_id=%s, article_id=%s)' % (
            uid, pid, aid))
        return None
    else:
        return res[0]


