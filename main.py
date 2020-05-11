
from flask import Flask, render_template, g
from pymongo import MongoClient

from data_source import TweetSource

app = Flask(__name__)


def g_factory(g):
    def decorator(func):
        name = func.__name__

        def result_func():
            if name not in g:
                setattr(g, name, func(g))
            return getattr(g, name)
        return result_func
    return decorator


@g_factory(g)
def get_db(g):
    client = MongoClient(f'mongodb://root:rootpassword@db:27017')
    return client.get_database('tweets')


@g_factory(g)
def get_test_collection(g):
    return get_db()['test1']


@g_factory(g)
def get_tweet_source(g):
    return TweetSource(get_db())


@app.route('/')
def hello():
    tweet_source = get_tweet_source()
    homepage = {
        group: [repr(tweet_source.get_tweets((group,)).to_data_frame()['text'])]
        for group in tweet_source.collection_names
    }
    return render_template('index.html', homepage=homepage)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
