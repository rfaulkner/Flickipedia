"""
Ryan Faulkner, 2014

Schema definitions for sqlalchemy
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """ Elements for Flickipedia users """

    __tablename__ = 'Users'

    _id = Column(Integer, primary_key=True, autoincrement=True)
    handle = Column(String(32))
    email = Column(String(24))
    firstname = Column(String(24))
    lastname = Column(String(24))
    password = Column(String(64))
    date_join = Column(Integer)

    def __repr__(self):
        return "<User(handle='%s', first='%s', last='%s')>" % (
            self.handle, self.firstname, self.lastname)


class Photo(Base):
    """ Elements for Flickr Photos """

    __tablename__ = 'Photos'

    _id = Column(Integer, primary_key=True, autoincrement=True)
    flickr_id = Column(Integer)
    article_id = Column(Integer)
    votes = Column(Integer)

    def __repr__(self):
        return "<Photo(photo='%s', article='%s', votes='%s')>" % (
            self.photo, self.article, self.votes)


class Article(Base):
    """ Elements for wiki articles """

    __tablename__ = 'Photos'

    _id = Column(Integer, primary_key=True, autoincrement=True)
    wiki_aid = Column(Integer)
    article_name = Column(String(32))

    def __repr__(self):
        return "<Article(name='%s', article='%s', votes='%s')>" % (
            self.article_name, self.article, self.votes)


class Like(Base):
    """ Elements for likes on article photos for flickr """

    __tablename__ = 'Likes'

    _id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    photo_id = Column(Integer)
    article_id = Column(Integer)

    def __repr__(self):
        return "<Like(user='%s', flickr_id='%s', article_id='%s')>" % (
            self.user_id, self.flickr_pid, self.article_id)