"""
    Author: Ryan Faulkner
    Date:   October 19th, 2014

    Container for mashup logic.
"""

import json
import random
from sqlalchemy.orm.exc import UnmappedInstanceError

from flickipedia.redisio import DataIORedis
from flickipedia.model.articles import ArticleModel, ArticleContentModel
from flickipedia.config import log, settings
from flickipedia.model.likes import LikeModel
from flickipedia.model.exclude import ExcludeModel
from flickipedia.model.photos import PhotoModel
from flickipedia.parse import parse_strip_elements, parse_convert_links, \
    handle_photo_integrate, format_title_link, add_formatting_generic


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


def handle_article_insert(article, wiki_page_id):
    """
    Handle insertion of article meta data
    :param article_id:  int; article id
    :return:            bool; success
    """
    with ArticleModel() as am:
        if am.insert_article(article, wiki_page_id):
            article_obj = am.get_article_by_name(article)
            article_id = article_obj._id
        else:
            log.error('Couldn\'t insert article: "%s"' % article)
            article_id = -1
    return article_id


def handle_article_content_insert(article_id, page_content, is_new_article):
    """
    Handle the insertion of article content
    :param article_id:      int; article id
    :param page_content:    json; page content
    :param is_new_article:  bool; a new article?
    :return:                bool; success
    """
    with ArticleContentModel() as acm:
        if is_new_article:
            acm.insert_article(article_id, json.dumps(page_content))
        else:
            acm.update_article(article_id, json.dumps(page_content))



def prep_page_content(article_id, article, wiki, photos, user_obj):
    """
    Prepare the formatted article content
    :param article_id:  int; article id
    :param article:     str; article name
    :param wiki_resp:   wikipedia; mediawiki api response
    :param photos:      list; list of photo json
    :param user_obj:    User; user object for request
    :return:            dict; formatted page response passed to jinja template
    """
    html = parse_strip_elements(wiki.html())
    html = parse_convert_links(html)
    html = add_formatting_generic(html)
    photo_ids = process_photos(article_id, photos)
    html = handle_photo_integrate(photos, html, article)
    page_content = {
        'title': format_title_link(wiki.title, article),
        'content': html,
        'section_img_class': settings.SECTION_IMG_CLASS,
        'num_photos': len(photos),
        'article_id': article_id,
        'user_id': user_obj.get_id(),
        'photo_ids': photo_ids
    }
    return page_content


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


def process_photos(article_id, photos, user_obj):
    """
    Handles linking photo results with the model and returns a list of
        Flickr photo ids to pass to templating
    :param article_id:  int; article id
    :param photos:  list of photos
    :param user_obj:    User; user object for request
    :return:    List of Flickr photo ids
    """
    photo_ids = []
    for photo in photos:
        # Ensure that each photo is modeled
        with PhotoModel() as pm:
            photo_obj = pm.get_photo(photo['photo_id'], article_id)
            if not photo_obj:
                log.info('Processing photo: "%s"' % str(photo))
                if pm.insert_photo(photo['photo_id'], article_id):
                    photo_obj = pm.get_photo(
                        photo['photo_id'], article_id)
                    if not photo_obj:
                        log.error('DB Error: Could not retrieve or '
                                  'insert: "%s"' % str(photo))
                        continue
                else:
                    log.error('Couldn\'t insert photo: "%s"'  % (
                        photo['photo_id']))
        photo['id'] = photo_obj._id
        photo['votes'] = photo_obj.votes
        # Retrieve like data
        with LikeModel() as lm:
            if lm.get_like(article_id, photo_obj._id,
                           user_obj.get_id()):
                photo['like'] = True
            else:
                photo['like'] = False

        photo_ids.append(photo['photo_id'])
    return photo_ids