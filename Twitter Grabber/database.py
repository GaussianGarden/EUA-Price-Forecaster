from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
from contextlib import contextmanager
import logging

logging.basicConfig(filename="log.txt", level=logging.DEBUG)
Base = declarative_base()
logger = logging.getLogger(__name__)


class Database(object):
    """A simple wrapper for an SQLite database with SQLAlchemy"""

    def __init__(self):
        """
        Make a database object
        """
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

    def add_objects(self, session, objects):
        """
        Add one or many objects to the database
        :param session: A database session
        :param objects: Either a single instance of an ORM class or an iterable of such
        """
        # Duck typing: Check if objects is an iterator
        try:
            for obj in objects:
                # ToDo: This causes an error if the object or any related objects are already in the database
                # (unique constraint violation). We need a way to update existing records instead of adding them again
                session.add(obj)
        except TypeError:
            # objects is not iterable, so just add it directly
            session.add(objects)
        except Exception as err:
            logger.exception(err)

    def update_objects(self, session, objects):
        """
        Update objects that already exist in the database
        :param session: A database session
        :param objects:
        :return: Either a single instance of an ORM class or an iterable of such
        """
        # ToDo: Implement this
        pass

