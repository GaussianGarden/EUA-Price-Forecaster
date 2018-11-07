from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base as Base
from sqlalchemy.orm import relationship


class Tweet(Base):
    """
    A basic ORM class for a Tweet class
    """
    __tablename__ = "tweets"
    id = Column(Integer, primary_key=True)
    text = Column(String(280))
    created_at = Column(Integer)
    language = Column(String(2))  # https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
    retweet_count = Column(Integer)
    favorite_count = Column(Integer)
    author_id = Column(Integer, ForeignKey("authors.id"))

    # Store a references to the author
    author = relationship("Author", back_populates="tweet")

    def __init__(self, id, text, created_at, language, retweet_count, favorite_count, author_id):
        self.id = id
        self.text = text
        self.created_at = created_at
        self.language = language
        self.retweet_count = retweet_count
        self.favorite_count = favorite_count
        self.author_id = author_id
