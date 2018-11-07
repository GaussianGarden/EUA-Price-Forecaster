from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base as Base
from sqlalchemy.orm import relationship


class Author(Base):
    """
    A basic ORM class for an Author class
    """
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True)
    description = Column(String(100))
    created_at = Column(Integer)
    favorites_count = Column(Integer)
    followers_count = Column(Integer)
    friends_count = Column(Integer)

    # Store tweets by this author
    tweets = relationship("Tweet", back_populates="author")

    def __init__(self, id, description, created_at, favorites_count, followers_count, friends_count):
        self.id = id
        self.description = description
        self.created_at = created_at
        self.favorites_count = favorites_count
        self.followers_count = followers_count
        self.friends_count = friends_count
