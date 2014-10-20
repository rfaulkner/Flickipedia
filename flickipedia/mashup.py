"""
    Author: Ryan Faulkner
    Date:   October 19th, 2014

    Container for mashup logic.
"""

import random
from sqlalchemy.orm.exc import UnmappedInstanceError

from flickipedia.redisio import DataIORedis
from flickipedia.model.articles import ArticleModel, ArticleContentModel
from flickipedia.config import log, settings
from flickipedia.model.likes import LikeModel
from flickipedia.model.exclude import ExcludeModel


def get_article_count():
    """
    Fetch total article count
    :return:    int; total count of articles
    """
    DataIORedis().connect()
    # Fetch article count from redis (query from DB if not present)
    # Refresh according to config for rate
    article_count = DataIORedis().read(settings.ARTICLE_COUNT_KEY)
    if not article_count \
            or random.randint(1, settings.ARTICLE_COUNT_REFRESH_RATE) == 1 \
            or article_count < settings.MYSQL_MAX_ROWS:
        with ArticleModel() as am:
            article_count = am.get_article_count()
            DataIORedis().write(settings.ARTICLE_COUNT_KEY, article_count)
    return int(article_count)


def get_max_article_id():
    """
    Fetch the maximum article ID
    :return:    int; maximum id from article meta
    """
    max_aid = DataIORedis().read(settings.MAX_ARTICLE_ID_KEY)
    if not max_aid \
            or random.randint(1, settings.ARTICLE_MAXID_REFRESH_RATE) == 1:
        with ArticleModel() as am:
            max_aid = am.get_max_id()
            DataIORedis().write(settings.MAX_ARTICLE_ID_KEY, max_aid)
    return max_aid


def get_article_stored_body(article):
    """
    Fetch corresponding article object
    :param article: str; article name
    :return:        json, Article; stored page content, corresponding
                                    article model object
    """
    with ArticleModel() as am:
        article_obj = am.get_article_by_name(article)
    try:
        with ArticleContentModel() as acm:
            body = acm.get_article_content(article_obj._id).markup
    except Exception as e:
        log.info('Article markup not found: "%s"' % e.message)
        body = ''
    return body


def get_wiki_content(article):
    """
    Retrieve the wiki content from the mediawiki API
    :param article: str; article name
    :return:        Wikipedia; mediawiki api response object
    """
    pass


def get_flickr_photos(flickr_json):
    """
    Retrience Flickr photo content from Flickr API
    :param article: str; article name
    :return:        list; list of Flickr photo json
    """
    photos = []
    for i in xrange(settings.NUM_PHOTOS_TO_FETCH):
        try:
            photos.append(
                {
                    'owner': flickr_json['photos']['photo'][i]['owner'],
                    'photo_id': flickr_json['photos']['photo'][i]['id'],
                    'farm': flickr_json['photos']['photo'][i]['farm'],
                    'server': flickr_json['photos']['photo'][i]['server'],
                    'title': flickr_json['photos']['photo'][i]['title'],
                    'secret': flickr_json['photos']['photo'][i]['secret'],
                },
            )
        except (IndexError, KeyError) as e:
            log.error('No more photos to process for: - "%s"' % (e.message))
        log.debug('Photo info: %s' % (str(photos)))
    return photos



def manage_article_storage(max_article_id, article_count):
    """
    Handle the storage of new articles
    :param max_article_id:  int; article id
    :param article_count:   int; total count of articles
    :return:                bool; success
    """
    if article_count >= settings.MYSQL_MAX_ROWS:
        if max_article_id:
            # TODO - CHANGE THIS be careful, could iterate many times
            article_removed = False
            while not article_removed:
                article_id = random.randint(0, int(max_article_id))
                with ArticleModel() as am:
                    log.info('Removing article id: ' + str(article_id))
                    try:
                        am.delete_article(article_id)
                        article_removed = True
                    except UnmappedInstanceError:
                        continue

        else:
            log.error('Could not determine a max article id.')
    return True


def handle_article_insert(article_id):
    """
    Handle insertion of article meta data
    :param article_id:  int; article id
    :return:            bool; success
    """
    pass


def handle_article_content_insert(article_id, page_content):
    """
    Handle the insertion of article content
    :param article_id:      int; article id
    :param page_content:    json; page content
    :return:                bool; success
    """
    pass


def prep_page_content(wiki_resp, photos):
    """
    Prepare the formatted article content
    :param wiki_resp:   wikipedia; mediawiki api response
    :param photos:      list; list of photo json
    :return:            dict; formatted page response passed to jinja template
    """
    pass


def update_last_access(article_id):
    """
    Update article last access
    :param article_id:  int; article id
    :return:            bool; success
    """
    pass


def order_photos_by_rank(article_id, photos):
    """ Reorders photos by score """
    # Compute scores
    for i in xrange(len(photos)):
        # Get Exclusions & Endorsements
        with ExcludeModel() as em:
            exclusions = em.get_excludes_article_photo(article_id,
                photos[i]['photo_id'])
        with LikeModel() as lm:
            endorsements = lm.get_likes_article_photo(article_id,
                photos[i]['photo_id'])
        photos[i]['score'] = len(endorsements) - len(exclusions)
    # lambda method for sorting by score descending
    f = lambda x, y: cmp(-x['score'], -y['score'])
    return sorted(photos, f)