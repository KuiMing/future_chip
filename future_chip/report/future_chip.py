import plotly.graph_objs as go
from ..process import FutureChangeProcessor


class FutureChipReport(FutureChangeProcessor):
    def __init__(self, today):
        super(FutureChipReport, self).__init__(today)
        self.get_change()

    def add_future_chip(self):
        df = self.report['option']['option_strength']
        Call = go.Table(
            domain=dict(x=[0, 0.5], y=[0.5, 0.75]),
            header=dict(
                values=list(df.Call.columns), fill=dict(color='#C2D4FF')),
            cells=dict(values=df.Call.values.T, fill=dict(color='#F5F8FF')))
        Put = go.Table(
            domain=dict(x=[0.5, 1], y=[0.5, 0.75]),
            header=dict(
                values=list(df.Put.columns), fill=dict(color='#C2D4FF')),
            cells=dict(values=df.Put.values.T, fill=dict(color='#F5F8FF')))
        putcall = go.Table(
            domain=dict(x=[0, 1], y=[0.75, 0.77]),
            header=dict(values=['Call', 'Put'], fill=dict(color='#C2D4FF')))

        df = self.report['option']['option_chip']
        option_chip = go.Table(
            domain=dict(x=[0, 1], y=[0.35, 0.55]),
            header=dict(values=list(df.columns), fill=dict(color='#C2D4FF')),
            cells=dict(values=df.values.T, fill=dict(color='#F5F8FF')))

        df = self.report['future']
        future = go.Table(
            domain=dict(x=[0, 1], y=[0.75, 0.95]),
            header=dict(values=list(df.columns), fill=dict(color='#C2D4FF')),
            cells=dict(values=df.values.T, fill=dict(color='#F5F8FF')))
        future_chip_data = [Call, Put, putcall, option_chip, future]
        return future_chip_data
