from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello():
    return "Dzień dobry z tej strony Małgorzata Żabińska-Rakoczy"
