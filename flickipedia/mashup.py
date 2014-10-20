"""
    Author: Ryan Faulkner
    Date:   October 19th, 2014

    Container for mashup logic.
"""

import random

from flickipedia.redisio import DataIORedis
from flickipedia.model.articles import ArticleModel, ArticleContentModel
from flickipedia.config import log, settings


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
    pass


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



def manage_article_storage(max_article_id):
    """
    Handle the storage of new articles
    :param max_article_id:  int; article id
    :return:                bool; success
    """
    pass


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