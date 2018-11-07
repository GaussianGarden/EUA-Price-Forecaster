from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database import Database
from database import Base
import logging


db = Database()
session = db._get_session()
logger = logging.getLogger(__name__)
logging.basicConfig(filename="log.txt", level=logging.DEBUG)


class Tweet(Base):
    """
    A basic ORM class for a Tweet class
    """
    __tablename__ = "tweets"
    id = Column(Integer, primary_key=True)
    text = Column(String(280))
    created_at = Column(Integer, index=True, unique=False)
    language = Column(String(2))  # https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
    retweet_count = Column(Integer)
    favorite_count = Column(Integer)
    author_id = Column(Integer, ForeignKey("authors.id"))

    # Store a references to the author
    author = relationship("Author", back_populates="tweets")

    def __init__(self, id, text, created_at, language, retweet_count, favorite_count, author_id):
        self.id = id
        self.text = text
        self.created_at = created_at
        self.language = language
        self.retweet_count = retweet_count
        self.favorite_count = favorite_count
        self.author_id = author_id


class Author(Base):
    """
    A basic ORM class for an Author class
    """
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True)
    description = Column(String(100))
    name = Column(String(30))
    screen_name = Column(String(30))
    created_at = Column(Integer)
    url = Column(String(100))
    status_count = Column(Integer)
    favorites_count = Column(Integer)
    followers_count = Column(Integer)
    friends_count = Column(Integer)

    # Store tweets by this author
    tweets = relationship("Tweet", back_populates="author")

    def __init__(self, id, description, name, screen_name, created_at, url, status_count, favorites_count,
                 followers_count, friends_count):
        self.id = id
        self.description = description
        self.name = name
        self.screen_name = screen_name
        self.created_at = created_at
        self.url = url
        self.status_count = status_count
        self.favorites_count = favorites_count
        self.followers_count = followers_count
        self.friends_count = friends_count


if __name__ == "__main__":
    logger.debug("Creating new tables.")
    db.create_new_tables()
    session.commit()
