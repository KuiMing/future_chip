from datetime import datetime
import urllib
import logging
import pandas as pd
import requests
import numpy as np
from .logger import logger


class future_chip_analysis():
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
        self.future = pd.read_csv(url, index_col=False)

    def get_option(self):
        url = '{}/optDataDown?down_type=1&commodity_id=TXO&{}&{}'.format(
            self._taifex_url, self._start_date, self._end_date)
        self.option = pd.read_csv(url, index_col=False)

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
        twse_summary.change = twse_summary.change.astype(float) * np.sign(
            twse_summary.change_percent.astype(float))
        self._twse_summary = twse_summary.drop(columns='dir')

    @property
    def last(self):
        return float(self.future['last'].iloc[0])

    @property
    def volume(self):
        volume = self.future['open_interest'][self.future['Trading Session'] ==
                                              'Regular']
        volume[volume == '-'] = 0
        return sum(volume.astype(float))

    @property
    def major_institutional_trader_volume(self):
        return sum(self._major_institutional_trader['Open Interest (Long)'])

    @property
    def taifex_close(self):
        return float(self._twse_summary.close.iloc[1].replace(',', ''))

    def putcall(self, putcall, contract):
        """
        :param putcall: "Put" or "Call"
        :type putcall: str
        :param contract: input "month"/"week" would get contract data of this month/week
        :type contract: str
        """
        if contract == 'week':
            deadline = self.option['Contract Month(Week)'].unique()[0]
        elif contract == 'month':
            deadline = self.option['Contract Month(Week)'].unique()[1]
        filtered = self.option[(self.option['Call/Put'] == putcall) & \
                                (self.option['Trading Session']=='Regular') & \
                                (self.option['Contract Month(Week)'] == deadline)]
        strike = filtered['Strike Price']
        settlemet = filtered['Settlement Price']
        if putcall == 'Put':
            strike = self.last - strike
        elif putcall == 'Call':
            strike = strike - self.last
        strike[strike > 0] = 0
        y = strike + settlemet.astype(float)
        return sum(y[y > 0])

    def __call__(self):
        try:
            self.get_twse_summary()
        except:
            logger.debug('{} is not trading date, please change.'.format(
                self._date))
            return
        self.get_future('TX')
        self.get_option()
        self.get_major_institutional_trader()