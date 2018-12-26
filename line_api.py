import os
import json
from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,
                            FlexSendMessage)
from future_chip import FutureChipReport, Figure, GetFutureRealtime

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


@app.route('/future_realtime')
def realtime():
    x = GetFutureRealtime()
    output, last = x.realtime_output()
    with open('config/now.json', 'r') as f:
        template = json.load(f)
        f.close()
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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    with open('config/table_figure.json', 'r') as j:
        bubble = json.load(j)
        j.close()
    line_bot_api.push_message(event.reply_token, TextSendMessage(text="Test"))
    if event.message.text == 'now':
        bubble = realtime()
        message = FlexSendMessage(alt_text="Report", contents=bubble)
        line_bot_api.reply_message(event.reply_token, message)
    else:
        try:
            global table
            table = table_html(event.message.text)
            global figure
            figure = figure_html(event.message.text)
            message = FlexSendMessage(alt_text="Report", contents=bubble)
            line_bot_api.reply_message(event.reply_token, message)
        except:
            text = event.message.text
        


if __name__ == "__main__":
    app.run()