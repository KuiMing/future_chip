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
        self.data[column] = self.data.close.ewm(
            span=window, adjust=False).mean()

    def DIF(self):
        self.EMA(12)
        self.EMA(26)
        self.data['DIF'] = self.data['12EMA'] - self.data['26EMA']
        change = self.data.DIF
        change[change < 0] = 0
        change[change > 0] = 1
        change = (change.values[1:] - change.values[:-1]).tolist()
        change.insert(0, 0)
        self.data['change'] = change