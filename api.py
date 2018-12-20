from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/test')
def test_page():
    return 'In test page!'


@app.route('/plotly.html')
def plotly():
    return render_template('plotly.html')
