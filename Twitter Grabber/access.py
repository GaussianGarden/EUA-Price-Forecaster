import twitter
import json
import logging
import os


class Accessor(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename="log.txt", level=logging.DEBUG)
        with open(os.path.join(os.getcwd(), "secrets", "secrets.json"), "r", encoding="utf-8") as f:
            self.secrets = json.load(f)["api"]
            masked_secrets = {key: value[:3] + ("*" * (len(value) - 3)) for key, value in self.secrets.items()}
            self.logger.debug("Created an API instance with {0}".format(masked_secrets))
            self.api = twitter.Api(**self.secrets)

    def get_tweets_by_user(self, screen_name, since_id=None, count=None):
        """
        Return tweets for the specified user. This is a wrapper for the twitter module function.
        :param screen_name: The screen name of the Twitter account
        :param since_id: Only consider tweets with IDs greater than this id
        :param count: Maximum number of tweets to request (maximum: 200)
        :return: A list of Status objects
        """
        try:
            statuses = self.api.GetUserTimeline(screen_name=screen_name, since_id=since_id, count=count)
            return statuses
        except Exception as err:
            self.logger.exception(err)
            return []
