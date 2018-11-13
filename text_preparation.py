from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import re

vec = TfidfVectorizer(strip_accents="unicode", lowercase=False)

re_collection = {
    "hashtags": re.compile(r"#(?P<hashtag>[\w]+)")
}


def extract_hashtags(sentence):
    return set(re_collection["hashtags"].findall(sentence))
