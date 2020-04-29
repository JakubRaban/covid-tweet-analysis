from flask import Flask, render_template
app = Flask(__name__)


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
