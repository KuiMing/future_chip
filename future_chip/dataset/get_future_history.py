import wget
import pandas as pd
import zipfile
from .get_future_chip import GetFutureChip

class GetFutureHistory():
    def __init__(self, date):
        self._date = date
        date = self._date.replace('/', '_')
        self.url = "http://www.taifex.com.tw/file/taifex/Dailydownload/DailydownloadCSV/Daily_{}.zip".format(date)
        self.file = "Daily_{}.csv".format(date)


    def download(self):
        wget.download(self.url, 'future.zip')  
        with zipfile.ZipFile('future.zip', 'r') as zip_ref:
            zip_ref.extractall('.')
    
    def read_csv(self):
        df = pd.read_csv(self.file, encoding='big5')
        df.商品代號 = [i.rstrip().lstrip() for i in df.商品代號]
        df['到期月份(週別)'] = [i.rstrip().lstrip() for i in df['到期月份(週別)']]
        df = df[df['到期月份(週別)'] == df['到期月份(週別)'].unique()[0]]
        df = df[df['成交日期'] == int(self._date.replace('/', ''))]
        df = df[df.商品代號 == 'TX']
        one_min_k = df.groupby(['成交時間'], as_index=False).max()
        one_min_k['open'] = df.groupby(['成交時間'], as_index=False).first()['成交價格']
        one_min_k['close'] = df.groupby(['成交時間'], as_index=False).last()['成交價格']
        one_min_k['low'] = df.groupby(['成交時間'], as_index=False).min()['成交價格']
        one_min_k = one_min_k.rename(columns={'成交價格':'high'})[['成交日期', '成交時間', 'open', 'close', 'high','low']]
        return one_min_k