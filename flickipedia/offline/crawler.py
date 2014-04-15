"""
Crawls Flickipedia to freshen indexes
"""

# Fixes issue with jinja template encoding in unicode
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import json
import random

from flickipedia.parse import parse_strip_elements, parse_convert_links
from flickipedia.redisio import DataIORedis, hmac

from flickipedia.config import log, settings, schema
from flickipedia.sources import flickr

import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError


class Crawler(object):

    def __init__(self):
        super(Crawler, self).__init__()

    def crawl(self):
        """ crawls the article space by choosing random links """
        article = 'lightning'
        while(1):
            links = self.process(article)
            article = links[random.randint(0, len(links))]


    def process(self, article):
        """
        Freshens the redis entry for `article`
        """

        DataIORedis().connect()

        key = hmac(article)

        # Get wiki
        try:
            wiki = wikipedia.WikipediaPage(article, preload=True)
        except DisambiguationError as e:
            # choose a disambiguation
            return
        except PageError as e:
            # bad page proceed with crawl
            return

        # extract & parse html
        html = parse_strip_elements(wiki.html())
        html = parse_convert_links(html)

        # Get flickr content
        res = flickr.call('photos_search', {'text': article,
                                            'format': 'json',
                                            'sort': 'relevance',
                                         })

        # TODO - detect failed responses
        res_json = json.loads(res[14:-1])

        # Extract data for the first photo returned
        owner = res_json['photos']['photo'][0]['owner']
        photo_id = res_json['photos']['photo'][0]['id']
        farm = res_json['photos']['photo'][0]['farm']
        server = res_json['photos']['photo'][0]['server']
        title = res_json['photos']['photo'][0]['title']
        secret = res_json['photos']['photo'][0]['secret']

        page_content = {
            'content': html,
            'owner': owner,
            'photo_id': photo_id,
            'farm': farm,
            'server': server,
            'title': title,
            'secret': secret
        }
        DataIORedis().write(key, json.dumps(page_content))

        # return the links
        return wiki.links

