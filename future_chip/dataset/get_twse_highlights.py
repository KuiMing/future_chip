import csv
import requests
import pandas as pd


class GetTwseHighlights():
    def __init__(self, date):
        self._date = date
        self._type = 'FMTQIK'
        self._twse_url = 'http://www.twse.com.tw/en/exchangeReport/{}?response=csv&date={}'.format(
            self._date, self._type)

    def get_highlights(self):
        download = requests.get(self._twse_url)
        decoded_content = download.content.decode('utf8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        TWII = []
        for row in my_list:
            TWII.append(row[:-1])
        for ii, i in enumerate(TWII[2:]):
            for index, j in enumerate(i):
                i[index] = j.replace(',', '')
            TWII[ii + 2] = i
        TWII = pd.DataFrame(TWII[2:-4], columns=TWII[1], dtype='float')
        return TWII