"""
This module handles functionality around entity ranking
"""

from flickipedia.model.likes import LikeModel
from flickipedia.model.exclude import ExcludeModel

def order_photos_by_rank(article_id, photos):
    """ Reorders photos by score """
    lm = LikeModel()
    em = ExcludeModel()

    # TODO - fill in computation & sort logic
    # Compute scores
    for photo in photos:
        # Get Exclusions

        # Get Endorsements
        # compute score
        pass
    # Apply sort
    return photos