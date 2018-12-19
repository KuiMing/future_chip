import pandas as pd
from ..dataset import GetFutureHistory


class FutureOhlcPreprocessor(GetFutureHistory):
    def __init__(self, date):
        super(FutureOhlcPreprocessor, self).__init__(date)
        # self._frequency = frequency
        self.download()
        self.read_csv()
        self.remove()

    def ohlc(self, frequency='5Min'):
        ohlc = self.tick.price.resample(frequency, label='right').ohlc()
        volume = self.tick.volume.resample(frequency, label='right').sum()
        ohlc['volume'] = volume
        return ohlc

    @property
    def is_long_short(self):
        Long = self.tick.price.last_valid_index() - self.tick.price.idxmax()
        Short = self.tick.price.last_valid_index() - self.tick.price.idxmin()
        return Long < Short

