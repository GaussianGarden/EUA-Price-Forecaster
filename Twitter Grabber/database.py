from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

Base = declarative_base()


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
        Session = sessionmaker(bind=self._get_engine())
        return Session()

    def create_new_tables(self):
        Base.metadata.create_all(self._get_engine())

    def add_objects(self, objects):
        session = self._get_session()
        for obj in objects:
            session.add(obj)
        session.commit()
        session.close()
