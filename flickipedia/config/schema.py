"""
Ryan Faulkner, 2014

Schema definitions for sqlalchemy
"""

from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """ Elements for Flickipedia users """

    __tablename__ = 'Users'

    _id = Column(BigInteger, primary_key=True, autoincrement=True)
    handle = Column(String(32), index=True)
    email = Column(String(24))
    firstname = Column(String(24))
    lastname = Column(String(24))
    password = Column(String(64))
    date_join = Column(Integer, index=True)

    def __repr__(self):
        return "<User(handle='%s', first='%s', last='%s')>" % (
            self.handle, self.firstname, self.lastname)


class Photo(Base):
    """ Elements for Flickr Photos """

    __tablename__ = 'Photos'

    _id = Column(BigInteger, primary_key=True, autoincrement=True)
    flickr_id = Column(BigInteger, index=True)
    article_id = Column(BigInteger, index=True)
    votes = Column(Integer)

    def __repr__(self):
        return "<Photo(photo='%s', article='%s', votes='%s')>" % (
            self.photo, self.article, self.votes)


class Article(Base):
    """ Elements for wiki articles """

    __tablename__ = 'Articles'

    _id = Column(BigInteger, primary_key=True, autoincrement=True)
    wiki_aid = Column(BigInteger, unique=True, index=True)
    article_name = Column(String(32))
    last_access = Column(Integer, index=True)

    def __repr__(self):
        return "<Article(name='%s', article='%s', votes='%s')>" % (
            self.article_name, self.article, self.votes)


class Like(Base):
    """ Elements for likes on article photos for flickr """

    __tablename__ = 'Likes'

    _id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, index=True)
    photo_id = Column(BigInteger, index=True)
    article_id = Column(BigInteger, index=True)

    def __repr__(self):
        return "<Like(user='%s', photo_id='%s', article_id='%s')>" % (
            self.user_id, self.photo_id, self.article_id)


class Exclude(Base):
    """ Elements for likes on article photos for flickr """

    __tablename__ = 'Exclusions'

    _id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, index=True)
    photo_id = Column(BigInteger, index=True)
    article_id = Column(BigInteger, index=True)

    def __repr__(self):
        return "<Exclude(user='%s', photo_id='%s', article_id='%s')>" % (
            self.user_id, self.photo_id, self.article_id)