import json
from contextlib import contextmanager

from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, or_, and_
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
        """
        Create a database engine object from a connection string
        :return: A database engine
        """
        return create_engine(self.connection_string)

    def _get_session(self):
        """
        Create a session with the bound database engine.
        :return: A session instance
        """
        Session = sessionmaker(bind=self._get_engine())
        return Session()

    @contextmanager
    def get_session(self):
        """
        Safely yield a session with a context manager. Before releasing the resource, all pending transactions are
        committed and the session is closed. This is the preferred way to yield a session.
        """
        logger.info("Acquiring session")
        session = self._get_session()
        try:
            yield session
            logger.debug("Committing session")
            session.commit()
        except Exception as err:
            logger.error("Rolling back")
            session.rollback()
            logger.exception(err)
            raise
        finally:
            logger.info("Closing session")
            session.close()

    def create_new_tables(self):
        """
        Update table metadata for the bound database engine
        """
        Base.metadata.create_all(self._get_engine())

    def add_objects(self, objects):
        session = self._get_session()
        for obj in objects:
            session.add(obj)
        session.commit()
        session.close()

    @staticmethod
    def get_tweets_by_ids(session, ids):
        tweets = session.query(Tweet).filter(Tweet.id.in_(ids))
        return {
            tweet.id: tweet
            for tweet in tweets
        }

    @staticmethod
    def get_authors_by_ids(session, ids):
        authors = session.query(Author).filter(Author.id.in_(ids))
        return {
            author.id: author
            for author in authors
        }

    @staticmethod
    def get_records_by_ids(session, mapper, ids):
        objs = session.query(mapper).filter(mapper.id.in_(ids))
        return {
            obj.id: obj
            for obj in objs
        }

    @staticmethod
    def get_author_count_data_as_of(session, id_as_of_pairs):
        query = session.query(AuthorCountData)
        or_clause = or_(*[and_(AuthorCountData.author_id == author_id, AuthorCountData.as_of == as_of)
                          for i, (author_id, as_of) in enumerate(id_as_of_pairs)])
        author_count_data_result = query.filter(or_clause)  # Why does "data" not have an explicit plural?
        result = {
            (author_count_data.author_id, author_count_data.as_of): author_count_data
            for author_count_data in author_count_data_result
        }
        return result

    # ToDo: Refactor this to avoid repetition
    def insert_or_update_statuses(self, session, status_list):
        tweet_ids = {status.id for status in status_list}
        tweet_dict = self.get_records_by_ids(session, Tweet, tweet_ids)
        author_ids = {status.user.id for status in status_list}
        author_dict = self.get_records_by_ids(session, Author, author_ids)
        id_as_of_pairs = {(status.user.id, status.created_at_in_seconds) for status in status_list}
        author_count_data_dict = self.get_author_count_data_as_of(session, id_as_of_pairs)
        for status in status_list:
            if status.id in tweet_dict:
                tweet_dict[status.id].update(status)
            else:
                new_tweet = Tweet.from_status(status)
                tweet_dict[status.id] = new_tweet
                session.add(new_tweet)
            if status.user.id in author_dict:
                author_dict[status.user.id].update(status)
            else:
                new_author = Author.from_status(status)
                author_dict[status.user.id] = new_author
                session.add(new_author)
            if (status.user.id, status.created_at_in_seconds) in author_count_data_dict:
                author_count_data_dict[(status.user.id, status.created_at_in_seconds)].update(status)
            else:
                new_author_count_data = AuthorCountData.from_status(status)
                author_count_data_dict[(status.user.id, status.created_at_in_seconds)] = new_author_count_data
                session.add(new_author_count_data)


class Tweet(Base):
    """
    A basic ORM class for a Tweet class
    """
    __tablename__ = "tweets"
    id = Column(Integer, primary_key=True)
    text = Column(String(280))
    created_at = Column(Integer, index=True, unique=False)
    language = Column(String(3))  # https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes takes 2 chars,
    # but Twitter uses "und" for "undefined" which uses 3 chars
    retweet_count = Column(Integer)
    favorite_count = Column(Integer)
    author_id = Column(Integer, ForeignKey("authors.id"))

    # Store a references to the author
    author = relationship("Author", back_populates="tweets")

    def __init__(self, tweet_id, text, created_at, language, retweet_count, favorite_count, author_id):
        self.id = tweet_id
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

    def update(self, status):
        self.text = status.text
        self.created_at = status.created_at_in_seconds
        self.language = status.lang
        self.retweet_count = status.retweet_count
        self.favorite_count = status.favorite_count
        self.author_id = status.user.id


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

    def __init__(self, author_id, description, name, screen_name, created_at, url):
        self.id = author_id
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

    def update(self, status):
        self.description = status.user.description
        self.name = status.user.name
        self.screen_name = status.user.screen_name
        self.created_at = timegm(parsedate(status.user.created_at))
        self.url = status.user.url


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

    def update(self, status):
        self.status_count = status.user.statuses_count
        self.favorites_count = status.user.favourites_count
        self.followers_count = status.user.followers_count
        self.friends_count = status.user.friends_count


if __name__ == "__main__":
    db = Database()
    logger.debug("Creating new tables.")
    db.create_new_tables()
