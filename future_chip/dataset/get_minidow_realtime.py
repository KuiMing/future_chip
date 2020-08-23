import re
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup
from .get_realtime import Quote, GetRealtime


class GetMinidowRealtime(GetRealtime):
    def __init__(self):
        super(GetMinidowRealtime, self).__init__()

        self.url = 'https://finance.yahoo.com/quote/YM%3DF?p=YM%3DF'

    def realtime_output(self):
        quote = Quote()
        html = requests.get(self.url)
        soup = BeautifulSoup(
            html.content, 'html.parser', from_encoding='utf-8')
        quote.name = "miniDow"

        links = soup.find_all("span", {
            "class": 'Trsdu(0.3s)',
            "data-reactid": "32"
        })
        reg = re.compile('>.*<')
        match = reg.search(str(links[0]))
        quote.trade_price = float(match.group(0)[1:-1].replace(',', ''))

        trade_time = soup.find_all("div", {"id": 'quote-market-notice'})
        reg = re.compile('[0-9]*:[0-9]{2}[A-Z]{2}')
        trade_time = datetime.strptime(
            reg.search(str(trade_time[0])).group(0), "%I:%M%p")
        quote.trade_time = trade_time

        links = soup.find_all("span", {
            "class": 'Trsdu(0.3s)',
            "data-reactid": "52"
        })
        reg = re.compile('>.*<')
        match = reg.search(str(links[0]))
        quote.open = match.group(0)[1:-1].replace(',', '')

        links = soup.find_all("td", {"data-reactid": '69'})
        reg = re.compile('>.*-')
        match = reg.search(str(links[0]))
        quote.low = match.group(0)[1:-1].replace(',', '').replace(' ', '')

        reg = re.compile('- .*<')
        match = reg.search(str(links[0]))
        quote.high = match.group(0)[1:-1].replace(',', '')

        links = soup.find_all(
            "span", {
                "class":
                'Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($positiveColor)',
                "data-reactid":
                "33"
            })
        reg = re.compile('>.*<')
        match = reg.search(str(links[0]))
        quote.change = match.group(0)[1:-1].replace(',', '')
        return quote
