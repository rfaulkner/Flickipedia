"""
This module defines exception classes for flickipedia
"""

class WikiAPICallError(Exception):
    """ Basic exception class for Wiki api calls """
    def __init__(self, message="Wiki api call error.", template="index.html",
                 options=None):
        Exception.__init__(self, message)
        self.template = template
        self.options = options


class FlickrAPICallError(Exception):
    """ Basic exception class for Flickr api calls"""
    def __init__(self, message="Flickr api call error.", template="index.html",
                 options=None):
        Exception.__init__(self, message)
        self.template = template
        self.options = options
