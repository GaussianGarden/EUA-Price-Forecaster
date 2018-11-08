import json

from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import logging
from email.utils import parsedate
from calendar import timegm

Base = declarative_base()
logger = logging.getLogger(__name__)
logging.basicConfig(filename="log.txt", level=logging.DEBUG)


class Database(object):
    """A simple wrapper for an SQLite database with SQLAlchemy"""

    def __init__(self):
        with open("config.json", "r", encoding="utf-8") as f:
            self.config = json.load(f)
        # ToDo: This might be incompatible with OS other than Windows...
        self.connection_string = "sqlite:///" + self.config["tweets_db"]["path"]

    def _get_engine(self):
        return create_engine(self.connection_string)

    def _get_session(self):
        try:
            return self._Session()
        except Exception:
            self._Session = sessionmaker(bind=self._get_engine())
        return self._Session()

    def create_new_tables(self):
        Base.metadata.create_all(self._get_engine())

    def add_objects(self, objects):
        session = self._get_session()
        for obj in objects:
            session.add(obj)
        session.commit()
        session.close()


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

    @staticmethod
    def from_status(status):
        return Tweet(
            status.id,
            status.text,
            status.created_at_in_seconds,
            status.lang,
            status.retweet_count,
            status.favorite_count,
            status.user.id
        )


class MinimalTweet(Base):
    """
    A class to represent minimal tweets, e.g. tweets that are not complete due to not being collected via the API
    """
    __tablename__ = "minimal_tweets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_name = Column(String(30))
    text = Column(String(280))

    def __init__(self, author_name, text):
        self.author_name = author_name
        self.text = text


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

    # Store tweets by this author
    tweets = relationship("Tweet", back_populates="author")

    # Store count data of this author
    count_data = relationship("AuthorCountData", back_populates="author", uselist=False)

    def __init__(self, id, description, name, screen_name, created_at, url):
        self.id = id
        self.description = description
        self.name = name
        self.screen_name = screen_name
        self.created_at = created_at
        self.url = url

    @staticmethod
    def from_status(status):
        return Author(
            status.user.id,
            status.user.description,
            status.user.name,
            status.user.screen_name,
            # We are using the same functionality as Status.created_at_in_seconds()
            # See here for source: https://python-twitter.readthedocs.io/en/latest/_modules/twitter/models.html#Status
            timegm(parsedate(status.user.created_at)),
            status.user.url
        )


class AuthorCountData(Base):
    """
    A class to store count data of authors (number of followers etc) as of a specific date
    """
    __tablename__ = "author_count_data"
    author_id = Column(Integer, ForeignKey("authors.id"), primary_key=True)
    as_of = Column(Integer, primary_key=True)
    status_count = Column(Integer)
    favorites_count = Column(Integer)
    followers_count = Column(Integer)
    friends_count = Column(Integer)

    author = relationship("Author", back_populates="count_data", uselist=False)

    def __init__(self, author_id, as_of, status_count, favorites_count, followers_count, friends_count):
        self.author_id = author_id
        self.as_of = as_of
        self.status_count = status_count
        self.favorites_count = favorites_count
        self.followers_count = followers_count
        self.friends_count = friends_count

    @staticmethod
    def from_status(status):
        return AuthorCountData(
            status.user.id,
            status.created_at_in_seconds,
            status.user.statuses_count,
            status.user.favourites_count,  # Caution: British English
            status.user.followers_count,
            status.user.friends_count
        )


if __name__ == "__main__":
    db = Database()
    logger.debug("Creating new tables.")
    db.create_new_tables()
