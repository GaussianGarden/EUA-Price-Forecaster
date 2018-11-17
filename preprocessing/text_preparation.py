from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import re

vec = TfidfVectorizer(strip_accents="unicode", lowercase=False)

re_collection = {
    "hashtags": re.compile(r"#(?P<hashtag>[\w]+)")
}


def extract_hashtags(sentence):
    """
    Find all words in a sentence that start with a pound symbol
    :param sentence: A single sentence
    :return: A set of words that begin with hashtags in the original sentence. The pound symbol is not present in the
    result set.
    """
    return set(re_collection["hashtags"].findall(sentence))


def extract_hashtags_from_corpus(corpus):
    """
    Get hashtags from the whole corpus as an iterator of sets
    :param corpus: An iterable of sentences
    :return: An iterator that yields the result of extract_hashtag for each sentence in the corpus, retaining the
    original order of sentences
    """
    for sentence in corpus:
        yield extract_hashtags(sentence)
