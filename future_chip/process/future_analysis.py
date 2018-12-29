from ..preprocess import FutureOhlcPreprocessor
from numpy import sign


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
    
    def DIF_sign(self):
        change = self.data.DIF.copy()
        change[change < 0] = 0
        change[change > 0] = 1
        change = (change.values[1:] - change.values[:-1]).tolist()
        change.insert(0, 0)
        self.data['sign'] = change

    def DIF_change(self):
        change = self.data.DIF.copy()
        change = (change.values[1:] - change.values[:-1]).tolist()
        change.insert(0, 0)
        change = sign(change)
        self.data['change'] = change
    
    def DIF(self):
        self.EMA(12)
        self.EMA(26)
        self.data['DIF'] = self.data['12EMA'] - self.data['26EMA']
        self.DIF_sign()
        self.DIF_change()

    def MACD(self):
        self.DIF()
        self.data['MACD'] = self.data.DIF.ewm(span=9, adjust=False).mean()
        self.data['OSC'] = self.data.DIF - self.data.MACD

    def __call__(self):
        self.SMA()
        self.MACD()