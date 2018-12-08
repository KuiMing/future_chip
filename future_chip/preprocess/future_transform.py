from datetime import datetime
from ..dataset import GetFutureChip


class FutureTrasformPreprocessor(GetFutureChip):
    def __init__(self, date):
        super(FutureTrasformPreprocessor, self).__init__(date)

    @property
    def is_settlement_date(self):
        return datetime.strptime(self._date, "%Y/%m/%d").weekday() == 2

    @property
    def last(self):
        if float(self.future['settlement_price'].iloc[0]) == 0:
            return float(self.future['settlement_price'].iloc[2])
        return float(self.future['settlement_price'].iloc[0])

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

    def option_chip(self, putcall, contract):
        """
        :param putcall: "Put" or "Call"
        :type putcall: str
        :param contract: input "month"/"week" would get contract data of this month/week
        :type contract: str
        """
        if self.is_settlement_date:
            index = 1
        else:
            index = 0
        if contract == 'week':
            deadline = self.option['Contract Month(Week)'].unique()[index]
            self.future = self.mtx
        elif contract == 'month':
            deadline = self.option['Contract Month(Week)'].unique()[index + 1]
            self.future = self.tx
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