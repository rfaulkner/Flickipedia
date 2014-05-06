"""

"""

from flickipedia.config import log, schema
from flickipedia.mysqlio import DataIOMySQL


class ArticleModel(object):

    def __init__(self):
        super(ArticleModel, self).__init__()

        self.io = DataIOMySQL()
        self.io.connect()

    def get_article_by_name(self, article):
        """
        Fetch Article

            :param article: str, article name

            :return:        Article schema object or None
        """
        schema_obj = getattr(schema, 'Article')
        res = self.io.session.query(schema_obj).filter(
            schema_obj.article_name == article).all()
        if len(res) > 0:
            return res[0]
        else:
            return None

    def insert_article(self, article, pageid):
        return self.io.insert('Article', wiki_aid=pageid, article_name=article)
