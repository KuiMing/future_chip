from datetime import datetime, timedelta
import pytz
import os
import time
import requests
import numpy as np
from bs4 import BeautifulSoup
from threading import Thread
from flask import Flask, request
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
collection = None

account = os.getenv('account')


class Quote(object):
    def __init__(self):
        self.name = None
        self.trade_time = None
        self.trade_price = None
        self.change = None
        self.open = None
        self.high = None
        self.low = None
        self.last = None

    def __str__(self):
        res = list()
        res.append(self.name)
        res.append(self.trade_time.strftime("%H:%M:%S"))
        res.append(self.trade_price)
        res.append(self.change)
        res.append(self.open)
        res.append(self.high)
        res.append(self.low)
        return str(res)


class GetRealtime():
    def realtime_output(self, last=None):
        quote = Quote()
        return quote, last

    def __call__(self):
        last = None
        while True:
            output, last = self.realtime_output(last)
            print(output.__str__())
            time.sleep(5)


class GetFutureRealtime(GetRealtime):
    def __init__(self):
        super(GetFutureRealtime, self).__init__()
        tz = pytz.timezone(pytz.country_timezones('tw')[0])
        now = datetime.now(tz)
        AH = now.hour >= 15 or now.hour < 8
        url_list = [
            'http://info512.taifex.com.tw/EN/FusaQuote_Norl.aspx',
            'http://info512ah.taifex.com.tw/EN/FusaQuote_Norl.aspx'
        ]
        self.url = url_list[AH]

    def realtime_output(self, last=None):
        html_data = requests.get(self.url)
        soup = BeautifulSoup(markup=html_data.text, features='html.parser')
        rows = soup.find_all('tr', {
            "class": "custDataGridRow",
            "bgcolor": "#DADBF7"
        })
        items = rows[0].find_all('td')
        name = items[0].a.text.strip()
        quote = Quote()
        quote.name = name
        quote.trade_price = float(items[6].font.text.replace(',', ''))
        quote.change = float(items[7].font.text.replace(',', ''))

        quote.trade_time = datetime.strptime(items[14].font.text, "%H:%M:%S")
        quote.open = float(items[10].font.text.replace(',', ''))
        quote.high = float(items[11].font.text.replace(',', ''))
        quote.low = float(items[12].font.text.replace(',', ''))
        return quote, last

def deal(text=''):
    r = requests.get(
        'https://calm-caverns-60140.herokuapp.com/deal?text={}'.format(text))
    return r.status_code


def matching(point, operation):
    point = int(point)
    os.system('echo define-end-time')
    buysell = operation
    tz = pytz.timezone(pytz.country_timezones('tw')[0])
    now = datetime.now(tz)
    if now.hour >= 15 and now.hour >= 15:
        date = datetime.date(now) + timedelta(days=1)
        end = datetime.strptime(date.strftime("%Y%m%d") + "0500", "%Y%m%d%H%M")
    elif now.hour < 8:
        date = datetime.date(now)
        end = datetime.strptime(date.strftime("%Y%m%d") + "0500", "%Y%m%d%H%M")
    else:
        end = datetime.strptime(
            datetime.date(now).strftime("%Y%m%d") + "1345", "%Y%m%d%H%M")
    os.system('echo define-buy-or-sell')
    profit = '-'
    if operation == 'cover':
        f = open(account)
        x = np.array([i.split(',') for i in f.read().split('\n')])
        last_order = x[x.T[-1] == 'deal'][-1][1]
        last = int(x[x.T[-1] == 'deal'][-1][2])
        f.close()
        if last_order == 'buy':
            profit = str(int(point) - last)
            buysell = 'sell'
        else:
            profit = str(last - int(point))
            buysell = 'buy'
    os.system('echo quote')    
    x = GetFutureRealtime()
    output, _ = x.realtime_output()
    price = output.trade_price
    if buysell == 'buy':
        while price >= point and datetime.now() < end:
            output, _ = x.realtime_output()
            price = output.trade_price
            os.system('echo price:{}'.format(price))
            time.sleep(5)
        done = price < point
    else:
        while price <= point and datetime.now() < end:
            output, _ = x.realtime_output()
            price = output.trade_price
            os.system('echo price: {}'.format(price))
            time.sleep(5)
        done = price < point
    if done:
        with open(account, 'a') as fd:
            fd.write('\n')
            date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            fd.write('{},{},{},{},{}'.format(date, operation, point, profit,
                                             'deal'))
            fd.close()
            deal('dealed')
    else:
        with open(account, 'a') as fd:
            fd.write('\n')
            date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            fd.write('{},{},{},{},{}'.format(date, operation, point, '-',
                                             'fail'))
            fd.close()
            deal('failed')

    os.system('bash $simulator')
    return done


class Record(Resource):
    def get(self):
        operation = request.args.get('operation', 'cover', type=str)
        point = request.args.get('point', type=str)
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        # order = '{},{},{},{},{}'.format(date, operation, point, '-', 'order')
        with open(account, 'a') as fd:
            fd.write('\n')
            fd.write('{},{},{},{},{}'.format(date, operation, point, '-',
                                             'order'))
            fd.close()

        os.system("echo recorded")
        os.system('bash $simulator')
        print('start to match')
        t = Thread(target=matching, args=(point, operation))
        t.start()
        return 'ok'


if __name__ == "__main__":
    api = Api(app)
    api.add_resource(Record, '/api/record')
    app.run(debug=True, host="0.0.0.0")
