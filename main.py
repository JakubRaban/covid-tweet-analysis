
from flask import Flask, render_template, g
from pymongo import MongoClient

app = Flask(__name__)


def get_db():
    if 'db' not in g:
        client = MongoClient('mongodb://root:rootpassword@db:27017')
        g.db = client.get_database('tweets')
    return g.db


def get_test_collection():
    if 'test_collection' not in g:
        g.test_collection = get_db()['test1']
    return g.test_collection


@app.route('/')
def hello():
    cursor = get_test_collection().find({})
    all_our_faults = [doc['fault'] for doc in cursor]
    return render_template('index.html', faults=all_our_faults)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
