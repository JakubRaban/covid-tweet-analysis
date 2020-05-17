
from flask import Flask, render_template, g
from pymongo import MongoClient

from data_source import TweetSource
import requests

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


def get_embeddable_tweet_html_by_id(tweet_id):
    r = requests.get('https://publish.twitter.com/oembed', params={'url': f'https://twitter.com/i/statuses/{tweet_id}',
                                                                   'maxwidth': 550})
    return r.json()['html']


@app.route('/')
def homepage_view():
    tweet_source = get_tweet_source()
    homepage = {
        group: [repr(tweet_source.get_tweets((group,)).to_data_frame()['text'])]
        for group in tweet_source.collection_names
    }
    users = [
        {
            'username': 'Andrzej Duda',
            'social_group': 'Politycy',
            'covid_tweet_count': 12,
            'average_favourites': 5000,
            'most_favourites': 17000,
            'average_retweets': 2000
        },
        {
            'username': 'Robert Biedroń',
            'social_group': 'Politycy',
            'covid_tweet_count': 53,
            'average_favourites': 800,
            'most_favourites': 3000,
            'average_retweets': 400
        },
        {
            'username': 'Dorota Gawryluk',
            'social_group': 'Dziennikarze',
            'covid_tweet_count': 102,
            'average_favourites': 590,
            'most_favourites': 1700,
            'average_retweets': 120
        }
    ]
    return render_template('homepage.html', homepage=homepage, users=users)


@app.route('/user-tweets')
def user_tweets_view():
    tweets = [
        {
            'date_published': '2020-01-09',
            'text': 'Żałosna jesteś w chuj dwulicowa nara'
        },
        {
            'date_published': '2020-01-10',
            'text': 'Hej chcesz coś z avonu'
        }
    ]
    embed_tweet_html = get_embeddable_tweet_html_by_id(get_db()['Lekarze'].find({})[0]['id_str'])
    return render_template('usertweets.html', tweets=tweets,
                           embedded_tweet=embed_tweet_html
                           )


@app.route('/tweet-test')
def tweet_test_view():
    t = get_db()['Lekarze'].find({})[0]['id_str']
    html = get_embeddable_tweet_html_by_id(t)
    return render_template('tweettest.html', xdd=html)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
