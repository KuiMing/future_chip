from datetime import datetime
import urllib
import logging
import pandas as pd
import requests
import numpy as np
from ..logger import logger


class GetFutureChip():
    """
    :param date: query date, for example: '2018/11/29'
    :type date: str
    """

    def __init__(self, date):
        self._date = date
        self._start_date = urllib.parse.urlencode({
            "queryStartDate": self._date
        })
        self._end_date = urllib.parse.urlencode({"queryEndDate": self._date})
        self._taifex_url = 'http://www.taifex.com.tw/enl/eng3'

    def get_future(self, target):
        """
        :param target: 'TX' or 'MTX'
        :type target: str
        """
        url = '{}/futDataDown?down_type=1&commodity_id={}&{}&{}'.format(
            self._taifex_url, target, self._start_date, self._end_date)
        return pd.read_csv(url, index_col=False)

    def get_option(self):
        url = '{}/optDataDown?down_type=1&commodity_id=TXO&{}&{}'.format(
            self._taifex_url, self._start_date, self._end_date)
        self.option = pd.read_csv(url, index_col=False)
        self.option['Contract Month(Week)'] = [
            str(i).rstrip().lstrip()
            for i in self.option['Contract Month(Week)']
        ]

    def get_major_institutional_trader(self):
        url = '{}/futContractsDateDown?&{}&{}&commodityId=TXF'.format(
            self._taifex_url, self._start_date, self._end_date)
        self._major_institutional_trader = pd.read_csv(url, index_col=False)

    def get_twse_summary(self):
        url = 'http://www.twse.com.tw/en/exchangeReport/MI_INDEX?response=json&date={}&type=MS'.format(
            self._date.replace('/', ''))
        r = requests.get(url)
        twse_summary = pd.DataFrame(
            r.json()['data1'],
            columns=['index', 'close', 'dir', 'change', 'change_percent'])
        twse_summary.change[twse_summary.change == '--'] = 0
        twse_summary.change_percent[twse_summary.change_percent == '--'] = 0
        twse_summary.change_percent[twse_summary.change_percent == '---'] = 0
        twse_summary.change = twse_summary.change.astype(float) * np.sign(
            twse_summary.change_percent.astype(float))
        self._twse_summary = twse_summary.drop(columns='dir')

    def __call__(self):
        try:
            self.get_twse_summary()
        except:
            logger.debug('{} is not trading date, please change.'.format(
                self._date))
            return
        self.tx = self.get_future('TX')
        self.mtx = self.get_future('MTX')
        self.get_option()
        self.get_major_institutional_trader()