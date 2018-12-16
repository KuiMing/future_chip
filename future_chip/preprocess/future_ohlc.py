import pandas as pd
from ..dataset import GetFutureHistory


class FutureOhlcPreprocessor(GetFutureHistory):
    def __init__(self, date):
        super(FutureOhlcPreprocessor, self).__init__(date)
        # self._frequency = frequency
        self.download()
        self.read_csv()

    def ohlc(self, frequency='5Min'):
        ohlc = self.tick.price.resample(frequency, label='right').ohlc()
        volume = self.tick.volume.resample(frequency, label='right').sum()
        ohlc['volume'] = volume
        return ohlc
