import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
import os
import sys
import pytz


class Quote(object):
    def __init__(self):
        self.name = None
        self.trade_time = None
        self.trade_price = None
        self.change = None
        self.open = None
        self.high = None
        self.low = None

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
    def realtime_output(self):
        quote = Quote()
        return quote

    def __call__(self):
        while True:
            output = self.realtime_output()
            print(output.__str__())
            time.sleep(5)