import json
import logging
import os
from calendar import timegm
from contextlib import contextmanager
from email.utils import parsedate

from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, or_, and_, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()
logger = logging.getLogger(__name__)
logging.basicConfig(filename="log.txt", level=logging.DEBUG)


class Database(object):
    """A simple wrapper for an SQLite database with SQLAlchemy"""

    def __init__(self):
        module_dir = os.path.dirname(os.path.realpath(__file__))
        config_path = os.path.join(module_dir, "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.connection_string = "sqlite:///" + "/".join([module_dir, "/".join(self.config["db"]["path"])])

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
        try:
            return self.Session()
        except AttributeError:
            self.Session = sessionmaker(bind=self._get_engine())
        return self.Session()

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

    @staticmethod
    def get_records_by_ids(session, mapper, ids):
        """
        Retrieve objects of the mapper class from the database given their unique ids
        :param session: An SQLAlchemy session
        :param mapper: The ORM class of the objects of interest (e.g. Tweet, Author, ...)
        :param ids: An iterable of IDs of interest
        :return: A dictionary of the form {id: object} for the intersection of the parameter "ids" and  ids that are
         actually persisted in the database
        """
        objs = session.query(mapper).filter(mapper.id.in_(ids))
        return {
            obj.id: obj
            for obj in objs
        }

    @staticmethod
    def get_author_count_data_as_of(session, id_as_of_pairs):
        """
        Return a dictionary of the form {(author_id, as_of): author_count_data_object} for AuthorCountData records
        from the database given an iterable of desired primary keys.
        :param session: An SQLAlchemy session
        :param id_as_of_pairs: An iterable of pairs of the form (id, as_of), i.e. the primary key of AuthorCountData
        :return: A dictionary of the form {(author_id, as_of): author_count_data_object} for AuthorCountData records
        from the database
        """
        query = session.query(AuthorCountData)
        or_clause = or_(*[and_(AuthorCountData.author_id == author_id, AuthorCountData.as_of == as_of)
                          for i, (author_id, as_of) in enumerate(id_as_of_pairs)])
        author_count_data_result = query.filter(or_clause)  # Why does "data" not have an explicit plural?
        result = {
            (author_count_data.author_id, author_count_data.as_of): author_count_data
            for author_count_data in author_count_data_result
        }
        return result

    def get_dicts_from_status_list(self, session, status_list):
        """
        Return a tuple of dicts for relevant data from the database
        :param session: An SQLAlchemy session
        :param status_list: An iterable of Status objects (from the Twitter module)
        :return: A tuple of dictionaries as in get_records_by_ids for Tweet, Author and AuthorCountData
        """
        tweet_ids, author_ids, id_as_of_pairs = \
            (Database._get_keys_from_status_list(status_list, lambda status: status.id),
             Database._get_keys_from_status_list(status_list, lambda status: status.user.id),
             Database._get_keys_from_status_list(status_list,
                                                 lambda status: (status.user.id, status.created_at_in_seconds)))
        return (self.get_records_by_ids(session, Tweet, tweet_ids),
                self.get_records_by_ids(session, Author, author_ids),
                self.get_author_count_data_as_of(session, id_as_of_pairs))

    @staticmethod
    def _get_keys_from_status_list(status_list, key_extractor):
        """
        Return a set of keys (in the database sense) from an iterable of Status objects
        :param status_list: An iterable of Status objects (from the Twitter module)
        :param key_extractor: A callable to extract relevant keys from a Status object
        :return: A set containing all the keys in the status_list, either as scalar or as tuple (if more than 1 value)
        """
        return {key_extractor(status) for status in status_list}

    @staticmethod
    def _compare_with_dict(session, status, mapper, dic, key_extractor):
        """
        Check if the given Status component (Tweet, Author, AuthorCountData) is in the dictionary containing database
        records. If so, update the existing record. Otherwise, create a new record and add it to the current session.
        :param session: An SQLAlchemy session
        :param status: A Status object (from Twitter module)
        :param mapper: The ORM class
        :param dic: A dictionary from _get_dicts_from_status_list
        :param key_extractor: A function to extract the desired object's key from a Status object
        :return: None
        """
        key = key_extractor(status)
        if key in dic:
            dic[key].update(status)
        else:
            new_record = mapper.from_status(status)
            dic[key] = new_record
            session.add(new_record)

    def insert_or_update_statuses(self, session, status_list):
        """
        Check the status_list for each contained Status object. If the related data is already in the database, update
        it. Otherwise, insert add it to the session. This mimics Django ORM's .save() method that intelligently either
        updates or inserts data.
        :param session: An SQLAlchemy session
        :param status_list: An iterable of Status objects (from Twitter module)
        :return: None
        """
        tweet_dict, author_dict, author_count_data_dict = self.get_dicts_from_status_list(session, status_list)
        for status in status_list:
            for (mapper, dic, key_extractor) in [(Tweet, tweet_dict, lambda state: state.id),
                                                 (Author, author_dict, lambda state: state.user.id),
                                                 (AuthorCountData, author_count_data_dict,
                                                  lambda state: (state.user.id, state.created_at_in_seconds))]:
                Database._compare_with_dict(session, status, mapper, dic, key_extractor)


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
        """
        Make a Tweet instance from A Status object
        :param status: A Status object (from Twitter module)
        :return: A Tweet instance representing that Status
        """
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
        """
        Make an Author instance from A Status object
        :param status: A Status object (from Twitter module)
        :return: An Author instance representing the user that created the Status
        """
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
        """
        Make an AuthorCountData instance from A Status object
        :param status: A Status object (from Twitter module)
        :return: An AuthorCountData instance representing the count data of the user that created the Status
        """
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


class CoreFinancialData(Base):
    """An ORM class to store financial data used for prediction"""
    __tablename__ = "core_financial_data"

    date = Column(Integer, primary_key=True)
    open = Column(Numeric(3))
    high = Column(Numeric(3))
    low = Column(Numeric(3))
    settle = Column(Numeric(3))
    change = Column(Numeric(3))
    volume = Column(Numeric(3))
    prev_day_open_interest = Column(Numeric(3))
    gas_open = Column(Numeric(3))
    gas_high = Column(Numeric(3))
    gas_low = Column(Numeric(3))
    gas_settle = Column(Numeric(3))
    gas_change = Column(Numeric(3))
    gas_volume = Column(Numeric(3))
    coal_open = Column(Numeric(3))
    coal_high = Column(Numeric(3))
    coal_low = Column(Numeric(3))
    coal_settle = Column(Numeric(3))
    coal_change = Column(Numeric(3))
    coal_volume = Column(Numeric(3))
    oil_open = Column(Numeric(3))
    oil_high = Column(Numeric(3))
    oil_low = Column(Numeric(3))
    oil_settle = Column(Numeric(3))
    oil_change = Column(Numeric(3))
    oil_volume = Column(Numeric(3))

    def __init__(self, date, ets_open, high, low, settle, change, volume, prev_day_open_interest, gas_open, gas_high,
                 gas_low, gas_settle, gas_change, gas_volume, coal_open, coal_high, coal_low, coal_settle, coal_change,
                 coal_volume, oil_open, oil_high, oil_low, oil_settle, oil_change, oil_volume):
        self.date = date
        self.open = ets_open
        self.high = high
        self.low = low
        self.settle = settle
        self.change = change
        self.volume = volume
        self.prev_day_open_interest = prev_day_open_interest
        self.gas_open = gas_open
        self.gas_high = gas_high
        self.gas_low = gas_low
        self.gas_settle = gas_settle
        self.gas_change = gas_change
        self.gas_volume = gas_volume
        self.coal_open = coal_open
        self.coal_high = coal_high
        self.coal_low = coal_low
        self.coal_settle = coal_settle
        self.coal_change = coal_change
        self.coal_volume = coal_volume
        self.oil_open = oil_open
        self.oil_high = oil_high
        self.oil_low = oil_low
        self.oil_settle = oil_settle
        self.oil_change = oil_change
        self.oil_volume = oil_volume


if __name__ == "__main__":
    db = Database()
    logger.debug("Creating new tables.")
    db.create_new_tables()
