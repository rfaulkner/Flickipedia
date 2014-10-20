"""
    Author: Ryan Faulkner
    Date:   October 19th, 2014

    Container for mashup logic.
"""


def get_article_count():
    """
    Fetch total article count
    :return:    int; total count of articles
    """
    pass


def get_max_article_id():
    """
    Fetch the maximum article ID
    :return:    int; maximum id from article meta
    """
    pass


def get_article_object(article):
    """
    Fetch corresponding article object
    :param article: str; article name
    :return:        Article; corresponding article model object
    """
    pass


def get_wiki_content(article):
    """
    Retrieve the wiki content from the mediawiki API
    :param article: str; article name
    :return:        Wikipedia; mediawiki api response object
    """
    pass


def get_flickr_photos(article):
    """
    Retrience Flickr photo content from Flickr API
    :param article: str; article name
    :return:        list; list of Flickr photo json
    """
    pass


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