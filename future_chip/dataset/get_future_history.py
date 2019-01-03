from datetime import datetime, timedelta
import wget
import pandas as pd
import zipfile
import os
from ..logger import logger
class GetFutureHistory():
    def __init__(self, date):
        self._date = date
        date = self._date.replace('/', '_')
        self.url = "http://www.taifex.com.tw/file/taifex/Dailydownload/DailydownloadCSV/Daily_{}.zip".format(date)
        self.file = "templates/Daily_{}.csv".format(date)


    def download(self):
        wget.download(self.url, 'templates/future.zip')
        try:
            with zipfile.ZipFile('templates/future.zip', 'r') as zip_ref:
                zip_ref.extractall('templates/.')
        except:
            os.remove('templates/future.zip')
            logger.info("There is no data for {}".format(self._date))
        
    def read_csv(self):
        df = pd.read_csv(self.file, encoding='big5', dtype={'到期月份(週別)':str})
        df.商品代號 = [i.rstrip().lstrip() for i in df.商品代號]
        df['到期月份(週別)'] = [i.rstrip().lstrip() for i in df['到期月份(週別)']]
        df = df[df.商品代號 == 'TX']
        df = df[df['到期月份(週別)'] == df['到期月份(週別)'].values[0]]
        df = df[df['成交日期'] == int(self._date.replace('/', ''))]
        df = df[df.成交時間 >=84500]
        dates = (df.成交日期.values[0]*1000000 + df.成交時間.values).astype(str)
        date = [datetime.strptime(x,'%Y%m%d%H%M%S') for x in dates]
        self.tick = pd.DataFrame({'price': df.成交價格.values, 'volume':df['成交數量(B+S)'].values/2}, index=date)
        
    def remove(self):
        os.remove('templates/future.zip')
        os.remove(self.file)

