from ..dataset import GetFutureChip


class FutureTrasformPreprocessor(GetFutureChip):
    def __init__(self, date):
        super(FutureTrasformPreprocessor, self).__init__(date)

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

    def option_chip(self, putcall, contract):
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