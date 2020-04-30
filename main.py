from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017')
db = client.get_database('tweets')


@app.route('/')
def hello():
    all_our_faults = [
        'U was jest pięć osób i trzeba żebyście mieli dużo',
        'To już by się przydało jakieś analizy przygototać',
        'Państwo chyba się skupiacie na innych projektach tudzież pracy zawodowej',
        'Te cele to o kant dupy rozbić',
        'Ten diagram Gantta to chyba tak na odczep się, nie zachodzi na siebie',
        'Łerkfloł jest zły',
        'Żródła należy sortować alfabetycznie'
    ]
    return render_template('index.html', faults=all_our_faults)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
