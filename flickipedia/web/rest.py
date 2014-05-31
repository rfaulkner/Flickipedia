"""
Defines restful interface to backend

"""

from flickipedia.mysqlio import DataIOMySQL
from flickipedia.config import schema
from flickipedia.config import log

from flickipedia.model.articles import ArticleModel
from flickipedia.model.photos import PhotoModel
from flickipedia.model.likes import LikeModel
from flickipedia.model.exclude import ExcludeModel


def api_insert_article(wiki_page_id, article_name):
    """
    Adds an article
    """
    raise NotImplementedError()


def api_insert_photo(flickr_id, article_id):
    """
    Adds a photo
    """
    raise NotImplementedError()


def api_set_like(uid, pid, aid):
    """
    Toggles the like-glyph value for the given triplet

    :param uid:     Flickipedia user id
    :param pid:     Flickipedia photo id
    :param aid:     Flickipedia article id

    :return:    True on success, False otherwise
    """

    io = DataIOMySQL()
    io.connect()

    result = api_get_like(uid, pid, aid)

    # toggle and set new value (delete row if it doesn't exist)
    if result:      # io.update false
        try:
            io.delete(result)
        except Exception as e:
            log.error(' "%s"' % e.message)
            return False

    else:           # io.update true
        try:
            io.insert('Like', user_id=uid, photo_id=pid, article_id=aid)
        except Exception as e:
            log.error(' "%s"' % e.message)
            return False

    return True


def api_get_like(uid, pid, aid):
    """
    Determines the like-glyph value for the given triplet

    :param uid:     Flickipedia user id
    :param pid:     Flickipedia photo id
    :param aid:     Flickipedia article id

    :return:    'Like' row if exists, None otherwise
    """
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


def api_method_endorse_event(article_id, user_id, photo_id):
    """model logic for photo endorse

    :param article_id:  article local id
    :param user_id:     user id
    :param photo_id:    photo local id
    """

    # Toggle like value in DB
    lm = LikeModel()
    like = lm.get_like(user_id, article_id, photo_id)

    if like:
        lm.delete_like(like)
    else:
        lm.insert_like(user_id, article_id, photo_id)
