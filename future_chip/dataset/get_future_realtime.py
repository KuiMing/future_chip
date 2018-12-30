import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
import os
import sys
import pytz
from .get_realtime import Quote, GetRealtime


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
        if last == None:
            quote.change = 0
        else:
            quote.change = quote.trade_price - last
        last = quote.trade_price

        quote.trade_time = datetime.strptime(items[14].font.text, "%H:%M:%S")
        quote.open = float(items[10].font.text.replace(',', ''))
        quote.high = float(items[11].font.text.replace(',', ''))
        quote.low = float(items[12].font.text.replace(',', ''))
        return quote, last
