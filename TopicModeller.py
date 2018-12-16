import re
from gensim import models, corpora
from nltk import word_tokenize
from nltk.corpus import stopwords
import sqlalchemy as db
import pandas as pd
from nltk.classify import SklearnClassifier
from sklearn.model_selection import train_test_split

# load data
engine = db.create_engine("sqlite://///Users/Chris/Documents/GitHub/EUA-Price-Forecaster/Data/database.db")
connection = engine.connect()
metadata = db.MetaData()
tweets = db.Table('tweets', metadata, autoload=True, autoload_with=engine)

# Select *
query = db.select([tweets])
ResultProxy = connection.execute(query)
results = pd.DataFrame(ResultProxy.fetchall())
results.columns = ResultProxy.keys()

# preparation
NUM_TOPICS = 10
STOPWORDS = stopwords.words('english')

data = []

for id in results:
    document = ' '.join(results["text"].values)
    data.append(document)


def clean_text(text):
    tokenized_text = word_tokenize(text.lower())
    cleaned_text = [t for t in tokenized_text if t not in STOPWORDS and re.match('[a-zA-Z\-][a-zA-Z\-]{2,}', t)]
    return cleaned_text


# For gensim we need to tokenize the data and filter out stopwords
tokenized_data = []
for text in data:
    tokenized_data.append(clean_text(text))

# Build a Dictionary - association word to numeric id
dictionary = corpora.Dictionary(tokenized_data)

# Transform the collection of texts to a numerical form
corpus = [dictionary.doc2bow(text) for text in tokenized_data]



# Build the LDA model
lda_model = models.LdaModel(corpus=corpus, num_topics=NUM_TOPICS, id2word=dictionary)


print("LDA Model:")

for idx in range(NUM_TOPICS):
    # Print the first 10 most representative topics
    print("Topic #%s:" % idx, lda_model.print_topic(idx, 10))

print("=" * 10)

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyser = SentimentIntensityAnalyzer()

def print_sentiment_scores(sentence):
    snt = analyser.polarity_scores(sentence)
    print("{:-<40} {}".format(sentence, str(snt)))

print_sentiment_scores(results.iloc[594,1])

