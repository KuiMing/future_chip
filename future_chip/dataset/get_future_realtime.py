import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
import os
import sys


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


class GetFutureRealtime():
    def __init__(self):
        AH = time.localtime().tm_hour >= 15 or time.localtime().tm_hour < 8
        url_list = [
            'http://info512.taifex.com.tw/EN/FusaQuote_Norl.aspx',
            'http://info512ah.taifex.com.tw/EN/FusaQuote_Norl.aspx'
        ]
        self.url = url_list[AH]

    def __call__(self):
        last = None
        while True:
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
            if last == None:
                quote.change = 0
            else:
                quote.change = quote.trade_price - last
            last = quote.trade_price

            quote.trade_time = datetime.strptime(items[14].font.text,
                                                 "%H:%M:%S")
            quote.open = float(items[10].font.text.replace(',', ''))
            quote.high = float(items[11].font.text.replace(',', ''))
            quote.low = float(items[12].font.text.replace(',', ''))
            print(quote)
            time.sleep(5)