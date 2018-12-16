from ..preprocess import FutureOhlcPreprocessor


class FutureAnalysisProcess(FutureOhlcPreprocessor):
    def __init__(self, date, frequency='5Min'):
        super(FutureAnalysisProcess, self).__init__(date)
        self.data = self.ohlc(frequency)

    def SMA(self, window=20):
        column = '{}SMA'.format(str(window))
        self.data[column] = self.data.close.rolling(window=window).mean()

    def EMA(self, window=12):
        column = '{}EMA'.format(str(window))
        self.data[column] = self.data.close.ewm(span=window, adjust=False).mean()
