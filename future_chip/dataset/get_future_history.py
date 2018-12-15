from datetime import datetime
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
        df = df[df['到期月份(週別)'] == self._date.replace('/', '')[:6]]
        df = df[df['成交日期'] == int(self._date.replace('/', ''))]
        df = df[df.商品代號 == 'TX']
        df = df[df.成交時間 >=84500]
        temp = df.groupby(['成交時間'], as_index=False).max()
        temp['open'] = df.groupby(['成交時間'], as_index=False).first()['成交價格']
        temp['close'] = df.groupby(['成交時間'], as_index=False).last()['成交價格']
        temp['low'] = df.groupby(['成交時間'], as_index=False).min()['成交價格']
        temp = temp.rename(columns={'成交價格':'high'})[['成交日期', '成交時間', 'open', 'close', 'high','low']]
        date = []
        for i in temp.成交時間:
            date.append(datetime.strptime(str(temp.成交日期.iloc[0]) + " " + str(i), "%Y%m%d %H%M%S"))
        output = pd.DataFrame({'open':temp.open.values, 'close':temp.close.values, 'high':temp.high.values, 'low':temp.low.values}, index=date)
        return output