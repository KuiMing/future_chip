import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
import os
import sys
import pytz
import json
from .get_realtime import Quote, GetRealtime


class GetFutureRealtime(GetRealtime):
    def __init__(self):
        super(GetFutureRealtime, self).__init__()
        tz = pytz.timezone(pytz.country_timezones('tw')[0])
        now = datetime.now(tz)
        AH = now.hour >= 15 or now.hour < 8
        payload = [
            '{"SymbolID":["TXFE1-F"]}',
            '{"SymbolID":["TXFE1-M"]}'
        ]
        self.url = "https://mis.taifex.com.tw/futures/api/getQuoteDetail"
        self.payload = payload[AH]
        
    def realtime_output(self):
        headers = {
          'Content-Type': 'application/json;charset=UTF-8',
        }
        response = requests.request("POST", self.url, 
                                    headers=headers, data=self.payload)
        res = json.loads(response.text)['RtData']['QuoteList'][0]
        
        quote = Quote()
        quote.name = res['DispEName']
            
        if res['CLastPrice'] == "":
            quote.change = ""
            quote.trade_price = ""
            quote.open = ""
            quote.high = ""
            quote.low = ""
            quote.trade_time = ""
        else:
            quote.trade_price = float(res['CLastPrice'])
            quote.open = float(res['COpenPrice'])
            quote.high = float(res['CHighPrice'])
            quote.low = float(res['CLowPrice'])
            quote.change = float(quote.trade_price) - float(quote.open)
            quote.trade_time = datetime.strptime(res['CTime'], "%H%M%S")
        return quote

