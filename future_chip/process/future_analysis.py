from ..preprocess import FutureOhlcPreprocessor


class FutureAnalysisProcess(FutureOhlcPreprocessor):
    def __init__(self, date, frequency='5Min'):
        super(FutureAnalysisProcess, self).__init__(date)
        self.data = self.ohlc(frequency)

    def moving_average(self, window=20):
        column = '{}MA'.format(str(window))
        self.data[column] = self.data.close.rolling(window=window).mean()
