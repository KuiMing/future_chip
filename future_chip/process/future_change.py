from datetime import datetime, timedelta
from math import floor
from numpy import concatenate
import pandas as pd
from ..preprocess import FutureTrasformPreprocessor
from ..dataset import GetFutureChip


class FutureChangeProcessor():
    def __init__(self, today):
        self._today = today
        self.last_date()

    def __repr__(self):
        self.get_change()

    def last_date(self):
        output = []
        count = 1
        while len(output) == 0:
            date = (datetime.strptime(self._today, '%Y/%m/%d') -
                    timedelta(days=count)).strftime('%Y/%m/%d')
            x = GetFutureChip(date)
            x.get_option()
            output = x.option
            count += 1
        self._last_date = date

    def putcall_difference(self, putcall):
        self.data_today.contract()
        self.data_today.atm()
        setattr(self.data_last_date, "contract_month", self.data_today.contract_month)
        setattr(self.data_last_date, "at_the_money", self.data_today.at_the_money)
        info = getattr(self.data_today, putcall + '_market')
        info_last = getattr(self.data_last_date, putcall + '_market')
        info['OI_last'] = info_last.OI
        info['difference'] = info.OI - info_last.OI
        return info

    @property
    def combine_call_put(self):
        call = self.putcall_difference('call')
        put = self.putcall_difference('put')
        array = concatenate([call.values, put.values], axis=1)
        header = pd.MultiIndex.from_product(
            [['Call', 'Put'], ['Strike Price', 'OI', 'OI_last', 'difference']], 
            names=['call/put', 'item'])
        return pd.DataFrame(array, columns=header)

    def adjust_before_settlement(self, future):
        pd.options.mode.chained_assignment = None
        transfer = self.data_today.nearby_volume + self.data_today.deferred_volume - self.data_last_date.nearby_volume - self.data_last_date.deferred_volume
        long_adjust = floor((self.data_today.institutional_long_volume / self.data_today.total_volume) * transfer)
        short_adjust = floor((self.data_today.institutional_short_volume / self.data_today.total_volume) * transfer)
        future.volume[future.item == 'total volume'] -= transfer
        future.volume[future.item == 'institutional long volume'] -= long_adjust
        future.volume[future.item == 'institutional short volume'] -= short_adjust
        future.volume[future.item == 'noninstitutional long volume'] = future.volume.iloc[0] - future.volume.iloc[3]
        future.volume[future.item == 'noninstitutional short volume'] = future.volume.iloc[0] - future.volume.iloc[4]
        return future

    def add_individual_and_major(self, future):
        ratio = self.data_today.individual_long_short * self.data_today.individual_ratio
        in_long = abs(future.difference.iloc[3]) * ratio
        in_short = abs(future.difference.iloc[4]) * -ratio
        future = future.append({'item': 'individual long', 'volume': None, 'difference': in_long}, ignore_index=True)
        future = future.append({'item': 'individual short', 'volume': None, 'difference': in_short}, ignore_index=True)
        future = future.append({'item': 'major long', 'volume': None, 'difference': future.difference.iloc[5] - in_long}, ignore_index=True)
        future = future.append({'item': 'major short', 'volume': None, 'difference': future.difference.iloc[6] - in_short}, ignore_index=True)
        return future

    def get_change(self):
        self.data_today = FutureTrasformPreprocessor(self._today)
        self.data_today()
        self.data_last_date = FutureTrasformPreprocessor(self._last_date, True)
        self.data_last_date()
        self.data_today.get_future_list()
        self.data_last_date.get_future_list()
        future = self.data_today.future_list.copy()
        if self.data_today.is_before_settlement and not self.data_today.is_month_settlement:
            future = self.adjust_before_settlement(future)
        future['difference'] = future['volume'] - self.data_last_date.future_list['volume']
        future = self.add_individual_and_major(future)
        self.report = {
            'future': future,
            'option':{
                'option_strength': self.combine_call_put, 
                'option_chip': pd.DataFrame(
                    {
                    'contract': list(self.data_today.settlement_price.keys()), 
                    'settlement': list(self.data_today.settlement_price.values()),
                    'call': [self.data_today.week_call_chip, self.data_today.month_call_chip],
                    'put': [self.data_today.week_put_chip, self.data_today.month_put_chip],
                    'ratio': [
                        self.data_today.week_call_chip / self.data_today.week_put_chip,
                        self.data_today.month_call_chip / self.data_today.month_put_chip,
                        ]
                    }
                    )}}



    
    
