from datetime import datetime, timedelta
from math import ceil, floor
import pandas as pd
from ..dataset import GetFutureChip


class FutureTrasformPreprocessor(GetFutureChip):
    def __init__(self, date):
        super(FutureTrasformPreprocessor, self).__init__(date)

    @property
    def is_settlement_date(self):
        return self.is_month_settlement or self.is_week_settlement

    @property
    def is_month_settlement(self):
        return float(self.tx['settlement_price'].iloc[0]) == 0

    @property
    def is_week_settlement(self):
        return float(self.mtx['settlement_price'].iloc[0]) == 0

    @property
    def is_before_settlement(self):
        return self.deferred_volume / self.total_volume >= 0.4

    @property
    def settlement_price(self):
        price = dict()
        if self.is_week_settlement:
            price['week'] = float(self.mtx['settlement_price'].iloc[2])
        else:
            price['week'] = float(self.mtx['settlement_price'].iloc[0])
        if self.is_month_settlement:
            price['month'] = float(self.tx['settlement_price'].iloc[2])
        else:
            price['month'] = float(self.tx['settlement_price'].iloc[0])
        return price

    @property
    def total_volume(self):
        volume = self.tx['open_interest'][self.tx['Trading Session'] ==
                                          'Regular']
        volume[volume == '-'] = 0
        return sum(volume.astype(float))

    @property
    def deferred_volume(self):
        return float(self.tx.open_interest[2])

    @property
    def nearby_volume(self):
        return float(self.tx.open_interest[0])

    @property
    def institutional_long_volume(self):
        return sum(self._major_institutional_trader['Open Interest (Long)'])

    @property
    def institutional_short_volume(self):
        return sum(self._major_institutional_trader['Open Interest (Short)'])

    @property
    def taifex_close(self):
        return float(self._twse_summary.close.iloc[1].replace(',', ''))

    def atm(self):
        self.at_the_money = [
            floor(self.taifex_close / 100) * 100,
            ceil(self.taifex_close / 100) * 100
        ]

    def contract(self):
        self.contract_month = [i for i in self.option['Contract Month(Week)'].unique() if len(i)==6][self.is_month_settlement]

    @property
    def call_market(self):
        option = self.option
        call = option[['Strike Price', 'OI']][(option['Call/Put'] == 'Call') & \
        (option['Contract Month(Week)'] == self.contract_month) & \
        (option['Trading Session'] == 'Regular') & \
        (option['Strike Price'] >= self.at_the_money[0]) & \
        (option['Strike Price'] <= self.at_the_money[0] + 700)].astype(float)
        call = call[call['Strike Price']%100 == 0].reset_index(drop=True)
        return call

    @property
    def put_market(self):
        option = self.option
        put = option[['Strike Price', 'OI']][(option['Call/Put'] == 'Put') & \
        (option['Contract Month(Week)'] == self.contract_month) & \
        (option['Trading Session'] == 'Regular') & \
        (option['Strike Price'] <= self.at_the_money[1]) & \
        (option['Strike Price'] >= self.at_the_money[1] - 700)].astype(float).sort_values('Strike Price', ascending=False)
        put = put[put['Strike Price']%100 == 0].reset_index(drop=True)
        return put

    @property
    def month_put_chip(self):
        return self.option_chip('Put', "month")

    @property
    def month_call_chip(self):
        return self.option_chip('Call', "month")

    @property
    def week_put_chip(self):
        return self.option_chip('Put', "week")

    @property
    def week_call_chip(self):
        return self.option_chip('Call', "week")
    
    @property
    def future_list(self):
        future = pd.DataFrame({
            'item': [
                'total volume', 'nearby volume', 'deferred volume',
                'institutional long volume', "institutional short volume",
                "noninstitutional long volume", "noninstitutional short volume"
            ],
            'volume': [
                self.total_volume, self.nearby_volume, self.deferred_volume,
                self.institutional_long_volume,
                self.institutional_short_volume,
                self.total_volume - self.institutional_long_volume,
                self.total_volume - self.institutional_short_volume
            ]
        })
        return future

    def option_chip(self, putcall, contract):
        """
        :param putcall: "Put" or "Call"
        :type putcall: str
        :param contract: input "month"/"week" would get contract data of this month/week
        :type contract: str
        """
        index = [0, 1]
        if contract == 'week':
            deadline = self.option['Contract Month(Week)'].unique()[index[
                self.is_settlement_date]]
        elif contract == 'month':
            deadline = self.contract_month

        filtered = self.option[(self.option['Call/Put'] == putcall) & \
                                (self.option['Trading Session']=='Regular') & \
                                (self.option['Contract Month(Week)'] == deadline)]
        strike = filtered['Strike Price']
        settlemet = filtered['Settlement Price']
        settlement_price = self.settlement_price
        if putcall == 'Put':
            strike = settlement_price[contract] - strike
        elif putcall == 'Call':
            strike = strike - settlement_price[contract]
        strike[strike > 0] = 0
        y = strike + settlemet.astype(float)
        return round(sum(y[y > 0]), 1)

