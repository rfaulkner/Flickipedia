"""
Ryan Faulkner, 2014

Schema definitions for sqlalchemy
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):

    __tablename__ = 'Users'

    uid = Column(Integer, primary_key=True, autoincrement=True)
    handle = Column(String(32))
    email = Column(String(24))
    firstname = Column(String(24))
    lastname = Column(String(24))
    password = Column(String(64))
    date_join = Column(Integer)

    def __repr__(self):
        return "<User(name='%s', fullname='%s', password='%s')>" % (
            self.name, self.fullname, self.password)
