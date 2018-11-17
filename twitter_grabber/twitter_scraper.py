import logging
import os
import twitter
from sqlalchemy import func
import database
from util import get_module_dir, get_local_json_file

logger = logging.getLogger(__name__)
logging.basicConfig(filename="log.txt", level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(filename)s %(funcName)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


class Accessor(object):

    def __init__(self):
        """
        Create an API Accessor object. This reads the secrets from the configuration and binds a twitter API object
        and a logger to the Accessor instance.
        """
        module_dir = get_module_dir(__file__)
        config = get_local_json_file(module_dir, "config.json")
        path_components = config["secrets_file"]["path"]
        config = get_local_json_file(os.path.join(module_dir, os.pardir), "config.json")
        self.relevant_accounts = config["relevant_accounts"]
        config = get_local_json_file(module_dir, os.path.join(*path_components))
        self.secrets = config["api"]
        masked_secrets = {key: value[:3] + ("*" * (len(value) - 3)) for key, value in self.secrets.items()}
        logger.debug("Created an API instance with {0}".format(masked_secrets))
        self.api = twitter.Api(**self.secrets)
        self.api.tweet_mode = "extended"  # If not set, tweets will be truncated after 140 characters

    def get_tweets_by_user(self, screen_name, since_id=None, max_id=None, count=None):
        """
        Return tweets for the specified user. This is a wrapper for the twitter module function.
        :param max_id: Maximum id of tweets to consider. If different from None, only tweets with an id <= max_id
        will be considered (that is, only older tweets)
        :param screen_name: The screen name of the Twitter account
        :param since_id: Only consider tweets with IDs greater than this id
        :param count: Maximum number of tweets to request (maximum: 200)
        :return: A list of Status objects
        """
        try:
            statuses = self.api.GetUserTimeline(screen_name=screen_name, since_id=since_id, max_id=max_id, count=count)
            return statuses
        except Exception as e:
            logger.exception(e)
            return []

    def get_maximum_tweet_id_per_account(self, sess):
        """
        Return the maximum saved tweet id per relevant account
        :param sess: An SQLAlchemy session instance
        :return: A dictionary of the form {screen_name: maximum_tweet_id_in_database} for each relevant account. If for
        any of these accounts no records are present in the database, the dictionary will not include this key.
        """
        query_result = sess.query(func.max(database.Tweet.id), database.Tweet).join(database.Author). \
            filter(database.Author.screen_name.in_(self.relevant_accounts)). \
            group_by(database.Tweet.author_id).all()
        return {
            tweet.author.screen_name: max_tweet_id
            for (max_tweet_id, tweet) in query_result
        }

    def get_all_tweets_since(self, db_instance, sess, tweets_per_call=200):
        """
        Fetch all tweets since most recent tweet in the database for all relevant accounts
        :param db_instance: A database instance
        :param sess: An SQLAlchemy session instance
        :param tweets_per_call: Number of statuses to fetch per individual call (limit is 200)
        :return: None
        """
        since_ids = self.get_maximum_tweet_id_per_account(sess)
        for screen_name in self.relevant_accounts:
            logger.info("Fetching Tweets for Screen Name @{0}.".format(screen_name))
            since_id = since_ids.get(screen_name) or 0
            max_id = None
            logger.info("Highest ID in database is {0} (0 = no record available).".format(since_id))
            while True:
                # Start by getting all tweets since since_id with no max_id passed. After receiving the tweets, max_id
                # will be updated and will be set to the minimum id received in that batch minus 1.
                # Thus, the next call will only fetch tweets prior to that tweet.
                tweets = self.get_tweets_by_user(screen_name, since_id=since_id, max_id=max_id, count=tweets_per_call)
                logger.info("Tweets received: {0}.".format(0 if tweets is None else len(tweets)))
                db_instance.insert_or_update_statuses(sess, tweets)
                sess.commit()
                if tweets is None or len(tweets) < tweets_per_call:
                    logger.info("Finished fetching for user {0}.".format(screen_name))
                    break
                else:
                    max_id = min(tweets, key=lambda status: status.id).id - 1
                    logger.info("Updated max_id to {0}.".format(max_id))
