import re
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup
from .get_future_realtime import Quote


class GetMinidowRealtime():
    def __init__(self):

        self.url = 'https://finance.yahoo.com/quote/YM%3DF?p=YM%3DF'

    def realtime_output(self, last=None):
        quote = Quote()
        html = requests.get(self.url)
        quote.trade_time = datetime.now()
        soup = BeautifulSoup(
            html.content, 'html.parser', from_encoding='utf-8')
        quote.name = "miniDow"

        links = soup.find_all("span", {
            "class": 'Trsdu(0.3s)',
            "data-reactid": "14"
        })
        reg = re.compile('>.*<')
        match = reg.search(str(links[0]))
        quote.trade_price = float(match.group(0)[1:-1].replace(',', ''))

        links = soup.find_all("span", {
            "class": 'Trsdu(0.3s)',
            "data-reactid": "24"
        })
        reg = re.compile('>.*<')
        match = reg.search(str(links[0]))
        quote.open = float(match.group(0)[1:-1].replace(',', ''))

        links = soup.find_all("td", {
            "class": 'Ta(end) Fw(b) Lh(14px)',
            "data-test": "DAYS_RANGE-value"
        })
        reg = re.compile('>.*-')
        match = reg.search(str(links[0]))
        quote.low = float(match.group(0)[1:-1].replace(',', ''))

        reg = re.compile('- .*<')
        match = reg.search(str(links[0]))
        quote.high = float(match.group(0)[1:-1].replace(',', ''))
        if last == None:
            quote.change = 0
        else:
            quote.change = quote.trade_price - last
        last = quote.trade_price
        return quote, last

    def __call__(self):
        last = None
        while True:
            output, last = self.realtime_output(last)
            print(output.__str__())
            time.sleep(5)
