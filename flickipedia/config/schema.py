"""
Ryan Faulkner, 2014

Schema definitions for sqlalchemy
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):

    __tablename__ = 'Users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
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

    __tablename__ = 'Photos'

    photo_id = Column(Integer, primary_key=True, autoincrement=True)
    article_name = Column(String(32))
    votes = Column(Integer)

    def __repr__(self):
        return "<Photo(photo='%s', article='%s', votes='%s')>" % (
            self.photo, self.article, self.votes)