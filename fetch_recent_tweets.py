import logging
import database
from twitter_grabber.twitter_scraper import Accessor

logger = logging.getLogger(__name__)
logging.basicConfig(filename="log.txt", level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(filename)s %(funcName)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


acc = Accessor()
db = database.Database()

with db.get_session() as session:
    try:
        acc.get_all_tweets_since(db, session, 200)
    except Exception as err:
        logger.exception(err)
