from flask import Flask, render_template
from flask import Flask, render_template, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
)
import requests
from datetime import datetime
import pytz
from bs4 import BeautifulSoup
import os
import sys
from future_chip import Quote, GetFutureRealtime
from future_chip import FutureChipReport

app = Flask(__name__)

linet = os.getenv('linet')
lines = os.getenv('lines')

line_bot_api = LineBotApi(linet)
handler = WebhookHandler(lines)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/test')
def test_page():
    return 'In test page!'


@app.route('/plotly.html')
def plotly():
    return render_template('plotly.html')


@app.route('/option_chip')
def option_chip():
    return render_template('option_chip.html')


@app.route('/future_realtime')
def realtime():
    x = GetFutureRealtime()
    return x()


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == 'now':
        text = realtime()
    else:
        try:
            x = FutureChipReport(event.message.text)
            x.add_html()
            text = 'line://app/1625409055-qZAO6DX0'
        except:
            text = event.message.text
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text))


if __name__ == "__main__":
    app.run()