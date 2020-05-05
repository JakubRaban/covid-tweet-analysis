
from flask import Flask, render_template, g
from pymongo import MongoClient

app = Flask(__name__)


def get_db():
    if 'db' not in g:
        client = MongoClient(f'mongodb://root:rootpassword@db:27017')
        g.db = client.get_database('tweets')
    return g.db


def get_test_collection():
    if 'test_collection' not in g:
        g.test_collection = get_db()['test1']
    return g.test_collection


@app.route('/')
def hello():
    group_tweets = get_db().collection_names()
    group_tweets.sort()
    homepage = {name: [doc['text'] for doc in get_db()[name].find({})[:10]] for name in group_tweets if name != 'test1'}
    return render_template('index.html', homepage=homepage)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
