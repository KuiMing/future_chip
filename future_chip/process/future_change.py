from datetime import datetime, timedelta
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
    
    @property
    def future_list(self, obj):
        future = {
            'item': [
                'total volume', 'nearby volume', 'deferred volume', 
                'institutional long volume', "institutional short volume",
                "noninstitutional long volume", "noninstitutional short volume"
                ],
            'volume':[
                obj.total_volume,
                obj.nearby_volume,
                obj.deferred_volume,
                obj.institutional_long_volume,
                obj.institutional_short_volume,
                obj.total_volume - obj.institutional_long_volume,
                obj.total_volume - obj.institutional_short_volume]
                }
        return future

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
            [['Call', 'Put'], ['Strike Price', 'OI', 'OI_last', 'differnce']], 
            names=['call/put', 'item'])
        return pd.DataFrame(array, columns=header)
        
    def get_change(self):
        self.data_today = FutureTrasformPreprocessor(self._today)
        self.data_today()
        self.data_last_date = FutureTrasformPreprocessor(self._last_date, True)
        self.data_last_date()
        future = self.data_today.future_list
        future['difference'] = future['volume'] - self.data_last_date.future_list['volume']
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



    
    
