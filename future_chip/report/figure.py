import os
from plotly.offline import plot
import plotly.graph_objs as go
from ..process import FutureAnalysisProcess


class Figure(FutureAnalysisProcess):
    def __init__(self, date, frequency):
        super(Figure, self).__init__(date, frequency)
        self._in_color = 'red'
        self._de_color = 'green'
        self.base()

    @property
    def colors(self):
        colors = []
        for i in range(len(self.data.close)):
            if i != 0:
                if self.data.close[i] > self.data.close[i - 1]:
                    colors.append(self._in_color)
                else:
                    colors.append(self._de_color)
            else:
                colors.append(self._de_color)
        return colors

    @property
    def candlestick(self):
        data = [dict(type='candlestick', open=self.data.open, high=self.data.high, low=self.data.low, \
        close=self.data.close, x=self.data.index, yaxis='y4', name='TX', \
        increasing=dict(line=dict(color=self._in_color)), decreasing=dict(line=dict(color=self._de_color)),)]
        return data

    def base(self):
        fig = dict(data=self.candlestick, layout=dict())
        fig['layout']['plot_bgcolor'] = 'rgb(250, 250, 250)'
        fig['layout']['xaxis'] = dict(
            rangeselector=dict(visible=False), rangeslider=dict(visible=False))
        fig['layout']['yaxis'] = dict(domain=[0, 0.2], showticklabels=False)
        fig['layout']['yaxis4'] = dict(domain=[0.2, 0.9])
        fig['layout']['legend'] = dict(
            orientation='h', y=0.9, x=0.3, yanchor='bottom')
        fig['layout']['margin'] = dict(t=40, b=40, r=40, l=40)
        fig['data'].append(
            dict(
                x=self.data.index,
                y=self.data.volume,
                marker=dict(color=self.colors),
                type='bar',
                yaxis='y',
                name='Volume'))
        self.basic_fig = fig
    
    def add_sma(self):
        self.basic_fig['data'].append(
            dict(
                x=self.data.index,
                y=self.data['20SMA'],
                marker=dict(color='#0085ff'),
                type='scatter',
                mode='lines',
                yaxis='y4',
                name='20SMA'))

    def add_subplot(self):
        if 'yaxis2' not in self.basic_fig['layout'].keys():
            self.basic_fig['layout']['yaxis2'] = dict(
                domain=[0.2, 0.35], showticklabels=False)
            self.basic_fig['layout']['yaxis4'] = dict(domain=[0.35, 0.9])
            self.added_sapce = 'y2'
        else:
            self.basic_fig['layout']['yaxis3'] = dict(
                domain=[0.35, 0.5], showticklabels=False)
            self.basic_fig['layout']['yaxis4'] = dict(domain=[0.5, 0.9])
            self.added_sapce = 'y3'

    def add_macd(self):
        self.MACD()
        self.add_subplot()
        df = self.data
        self.basic_fig['data'].append(
            dict(
                x=df.index,
                y=df.DIF,
                type='scatter',
                mode='lines',
                line=dict(width=1),
                marker=dict(color='#E377C2'),
                yaxis=self.added_sapce,
                name='DIF'))
        self.basic_fig['data'].append(
            dict(
                x=df.index,
                y=df.MACD,
                type='scatter',
                mode='lines',
                line=dict(width=1),
                marker=dict(color='#FFD700'),
                yaxis=self.added_sapce,
                name='MACD'))
        self.basic_fig['data'].append(
            dict(
                x=df.index,
                y=df.OSC,
                marker=dict(color=self.colors),
                type='bar',
                yaxis=self.added_sapce,
                name='OSC'))

    def add_dif_change(self):
        self.DIF()
        self.add_subplot()
        df = self.data
        self.basic_fig['data'].append(
            dict(
                x=df.index,
                y=df.sign,
                type='scatter',
                mode='lines',
                line=dict(width=1),
                marker=dict(color='#FF0000'),
                yaxis=self.added_sapce,
                name='sign'))
        self.basic_fig['data'].append(
            dict(
                x=df.index,
                y=df.change,
                type='scatter',
                mode='lines',
                line=dict(width=1),
                marker=dict(color='#0085ff'),
                yaxis=self.added_sapce,
                name='change'))

    def writer(self, path='.', filename='plotly_candlestick'):
        # date = self._date.replace('/', '')
        filename = os.path.join(path, '{}.html'.format(filename))
        plot(
            self.basic_fig,
            filename=filename,
            validate=False)
