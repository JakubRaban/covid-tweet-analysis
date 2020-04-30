
from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('mongodb://root:rootpassword@db:27017')
db = client.get_database('tweets')
collection = db['test1']


@app.route('/')
def hello():
    cursor = collection.find({})
    all_our_faults = [doc['fault'] for doc in cursor]
    return render_template('index.html', faults=all_our_faults)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
