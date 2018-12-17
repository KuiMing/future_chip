from .figure import Figure
from .future_chip import FutureChipReport


class MergeReport(Figure):
    def __init__(self, date, frequency):
        super(MergeReport, self).__init__(date, frequency)
        future_chip = FutureChipReport(self._date)
        self.future_chip = future_chip.add_future_chip()
        self.__call__()
        self.add_macd()
        self.add_dif_change()

    def merge(self):
        fig = self.basic_fig
        fig['layout']['height'] = 1400
        fig['layout']['yaxis4']['domain'] = [
            i / 2 for i in fig['layout']['yaxis4']['domain']
        ]
        fig['layout']['yaxis']['domain'] = [
            i / 2 for i in fig['layout']['yaxis']['domain']
        ]
        fig['layout']['yaxis2']['domain'] = [
            i / 2 for i in fig['layout']['yaxis2']['domain']
        ]
        fig['layout']['yaxis3']['domain'] = [
            i / 2 for i in fig['layout']['yaxis3']['domain']
        ]
        fig['layout']['legend']['y'] /= 2
        fig['data'].extend(self.future_chip)
