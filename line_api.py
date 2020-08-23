from datetime import datetime
import os
from io import BytesIO
import glob
import json
import time
from PIL import Image
import requests
from twstock import Stock
import twstock
from flask import Flask, request, abort, send_file
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,
                            FlexSendMessage)
from future_chip import FutureChipReport, Figure, GetFutureRealtime, GetMinidowRealtime

app = Flask(__name__)

linet = os.getenv('linet')
lines = os.getenv('lines')
lineid = os.getenv('lineid')
simulator_recorder = os.getenv('simulator_recorder')
line_bot_api = LineBotApi(linet)
handler = WebhookHandler(lines)


@app.route('/')
def TXO_chart():
    x = GetFutureRealtime()
    target = x.realtime_output().name
    url = x.url.replace('EN/FusaQuote_Norl.aspx',
                        '') + 'Future/chart.aspx?type=1&size=630400&contract='
    response = requests.get('{}{}'.format(url, target))
    img = Image.open(BytesIO(response.content))
    output = BytesIO()
    img.convert('RGBA').save(output, format='PNG')
    output.seek(0, 0)
    return send_file(output, mimetype='image/png', as_attachment=False)


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


def simulate_output(order, point):
    x = GetFutureRealtime()
    output = x.realtime_output()
    with open('config/simulator.json', 'r') as f:
        template = json.load(f)
        f.close()
    template['body']['contents'][0]['text'] = order + output.name
    template['body']['contents'][2]['contents'][0]['contents'][1][
        'text'] = output.trade_time.strftime("%H:%M:%S")
    template['body']['contents'][2]['contents'][1]['contents'][1][
        'text'] = str(output.trade_price)
    template['body']['contents'][2]['contents'][2]['contents'][1][
        'text'] = point
    profit = output.trade_price - int(point)
    if order == 'sell':
        profit = -profit
    elif order == 'cover':
        profit = '-'
    template['body']['contents'][2]['contents'][3]['contents'][1][
        'text'] = str(profit)
    return template


@app.route('/quotation')
def quotation():
    with open('config/quotation.json', 'r') as f:
        template = json.load(f)
        f.close()
    template['contents'].append(tx())
    template['contents'].append(minidow())
    return template


@app.route('/future_realtime')
def tx():
    x = GetFutureRealtime()
    output = x.realtime_output()
    template = realtime(output)
    return template


@app.route('/minidow_realtime')
def minidow():
    # try:
    x = GetMinidowRealtime()
    output = x.realtime_output()
    template = realtime(output)
    # except:
    #     with open('config/now.json', 'r') as f:
    #         template = json.load(f)
    #         f.close()
    #     template['body']['contents'][0]['text'] = 'Mini Dow'
    #     template['body']['contents'][2]['contents'][0]['contents'][1][
    #         'text'] = datetime.now().strftime("%H:%M:%S")
    return template


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print(body)
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


def component(text, color):
    q = {"type": "text", "text": str(text), "size": "xs", "color": color}
    return q


def stock_query(code, temp):
    stock = Stock(code)
    x = twstock.realtime.get(code)
    hour = datetime.now().hour + 8
    if hour < 14 and hour >= 9:
        change = round(
            float(x['realtime']['latest_trade_price']) - float(
                stock.price[-1]), 2)
    else:
        change = round(
            float(x['realtime']['latest_trade_price']) - float(
                stock.price[-2]), 2)

    if change < 0:
        color = '#2d8540'
    elif change > 0:
        color = '#F25702'
    else:
        color = '#111111'
    temp['body']['contents'][2]['contents'][0]['contents'].append(
        component(x['info']['code'], color))
    temp['body']['contents'][2]['contents'][1]['contents'].append(
        component(x['realtime']['latest_trade_price'], color))
    temp['body']['contents'][2]['contents'][2]['contents'].append(
        component(x['realtime']['open'], color))
    temp['body']['contents'][2]['contents'][3]['contents'].append(
        component(change, color))
    temp['body']['contents'][2]['contents'][4]['contents'].append(
        component(x['realtime']['high'], color))
    temp['body']['contents'][2]['contents'][5]['contents'].append(
        component(x['realtime']['low'], color))
    return temp


def stock_qoutation():
    with open('config/stock.json', 'r') as f:
        temp = json.load(f)
        f.close()
    with open('config/stock_list.json', 'r') as f:
        stock_list = json.load(f)
        f.close()
    for i in stock_list['stock']:
        temp = stock_query(i, temp)
    return temp


@app.route('/deal')
def send_deal_message():
    text = request.args.get('text', 'dealed', type=str)
    line_bot_api.push_message(lineid, TextSendMessage(text=text))
    return 'ok'


@app.route('/logistic')
def send_logistic_message():
    text = request.args['text']
    userid = request.args['userid']
    line_bot_api.push_message(userid, TextSendMessage(text=text))
    return 'ok'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    with open('config/table_figure.json', 'r') as j:
        bubble = json.load(j)
        j.close()
    line_input = event.message.text.split(' ')
    operation = ['buy', 'sell', 'cover']

    if event.message.text == 'TX':
        bubble = quotation()
        message = FlexSendMessage(alt_text="Report", contents=bubble)
        line_bot_api.reply_message(event.reply_token, message)
    elif event.message.text == 'Mini Dow':
        bubble = minidow()
        message = FlexSendMessage(alt_text="Report", contents=bubble)
        line_bot_api.reply_message(event.reply_token, message)
    elif event.message.text == 'stock':
        bubble = stock_qoutation()
        message = FlexSendMessage(alt_text="Report", contents=bubble)
        line_bot_api.reply_message(event.reply_token, message)
    elif line_input[0] in operation:
        r = requests.get("{}?operation={}&point={}".format(
            simulator_recorder, line_input[0], line_input[1]))
        bubble = simulate_output(line_input[0], line_input[1])
        message = FlexSendMessage(alt_text="Report", contents=bubble)
        line_bot_api.reply_message(event.reply_token, message)
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
