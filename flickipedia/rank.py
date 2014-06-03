"""
This module handles functionality around entity ranking
"""

from flickipedia.model.likes import LikeModel
from flickipedia.model.exclude import ExcludeModel


def order_photos_by_rank(article_id, photos):
    """ Reorders photos by score """
    lm = LikeModel()
    em = ExcludeModel()

    # Compute scores
    for i in xrange(len(photos)):
        # Get Exclusions & Endorsements
        exclusions = em.get_excludes_article_photo(article_id, photos['id'])
        endorsements = lm.get_likes_article_photo(article_id, photos['id'])
        photos[i]['score'] = len(endorsements) - len(exclusions)

    f = lambda x: x['score']
    return sorted(photos, f)
