import os
import glob
import json
from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,
                            FlexSendMessage)
from future_chip import FutureChipReport, Figure, GetFutureRealtime, GetMinidowRealtime
import requests

app = Flask(__name__)

linet = os.getenv('linet')
lines = os.getenv('lines')
simulator_recorder = os.getenv('simulator_recorder')
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
    date = request.args.get('date', '', type=str)
    if date == '':
        return figure
    else:
        figured = figure_html(date)
        return figured


@app.route('/future_option')
def future_option():
    date = request.args.get('date', '', type=str)
    if date == '':
        return table
    else:
        tabled = table_html(date)
        return tabled


def realtime(output):
    with open('config/now.json', 'r') as f:
        template = json.load(f)
        f.close()
    template['body']['contents'][0]['text'] = output.name
    template['body']['contents'][2]['contents'][0]['contents'][1][
        'text'] = output.trade_time.strftime("%H:%M:%S")
    template['body']['contents'][2]['contents'][1]['contents'][1][
        'text'] = str(output.trade_price)
    template['body']['contents'][2]['contents'][2]['contents'][1][
        'text'] = str(output.open)
    template['body']['contents'][2]['contents'][3]['contents'][1][
        'text'] = str(output.high)
    template['body']['contents'][2]['contents'][4]['contents'][1][
        'text'] = str(output.low)
    template['body']['contents'][2]['contents'][5]['contents'][1][
        'text'] = str(output.change)
    return template


@app.route('/future_realtime')
def tx():
    x = GetFutureRealtime()
    output = x.realtime_output()
    template = realtime(output[0])
    return template


@app.route('/minidow_realtime')
def minidow():
    x = GetMinidowRealtime()
    output = x.realtime_output()
    template = realtime(output[0])
    return template


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


def table_html(date):
    x = FutureChipReport(date)
    table = x.add_html()
    return table


def figure_html(date):
    x = Figure(date, "5Min")
    x.add_macd()
    x.add_dif_change()
    x.writer('templates', filename='plotly')
    with open('templates/plotly.html', 'r') as f:
        figure = f.read()
        f.close()
    return figure


def remove_zip_file():
    try:
        files = glob.glob('templates/future*.zip')
        for i in files:
            os.remove(i)
    except:
        pass


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    with open('config/table_figure.json', 'r') as j:
        bubble = json.load(j)
        j.close()
    line_input = event.message.text.split(' ')
    operation = ['buy', 'sell', 'cover']

    if event.message.text == 'TX':
        bubble = tx()
        message = FlexSendMessage(alt_text="Report", contents=bubble)
        line_bot_api.reply_message(event.reply_token, message)
    elif event.message.text == 'Mini Dow':
        bubble = minidow()
        message = FlexSendMessage(alt_text="Report", contents=bubble)
        line_bot_api.reply_message(event.reply_token, message)
    elif line_input[0] in operation:
        r = requests.get("{}?operation={}&point={}".format(simulator_recorder, line_input[0], line_input[1]))
        text = "https://kuiming.gitbook.io/future-simulate-record/account"
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=text))
    else:
        try:
            remove_zip_file()
            global table
            table = table_html(event.message.text)
            global figure
            figure = figure_html(event.message.text)
            message = FlexSendMessage(alt_text="Report", contents=bubble)
            line_bot_api.reply_message(event.reply_token, message)
        except:
            text = event.message.text
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=text))


if __name__ == "__main__":
    app.run()