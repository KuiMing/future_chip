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
            domain=dict(x=[0, 1], y=[0.45, 0.575]),
            header=dict(values=list(df.columns), fill=dict(color='#C2D4FF')),
            cells=dict(values=df.values.T, fill=dict(color='#F5F8FF')))

        df = self.report['future']
        future = go.Table(
            domain=dict(x=[0, 1], y=[0.75, 1]),
            header=dict(values=list(df.columns), fill=dict(color='#C2D4FF')),
            cells=dict(values=df.values.T, fill=dict(color='#F5F8FF')))
        future_chip_data = [Call, Put, putcall, option_chip, future]
        return future_chip_data

    def html(self,
             df,
             index=True,
             fontsize=40,
             mode='w',
             title=None,
             filename='option_chip.html'):
        fontsize = str(fontsize) + 'pt'
        if index:
            output = df.style \
                    .set_table_styles([{'selector': 'th', 'props': [('font-size', fontsize)]}])
        else:
            output = df.style \
            .set_table_styles([{'selector': 'th', 'props': [('font-size', fontsize)]},
                                {'selector': '.row_heading', 'props': [('display', 'none')]},
                                {'selector': '.blank.level0', 'props': [('display', 'none')]}])
        output = output.set_properties(**{'font-size': fontsize, 'font-family': 'Calibri'}) \
        .set_table_attributes('border="5" class="dataframe table table-hover table-bordered"') \
        .render()
        output = '<font size=40>{} {}</font>{}'.format(self._today, title,
                                                       output)
        return output

    def add_html(self):
        output = self.html(self.report['future'], index=False, title='Future Volume Change') + \
        self.html(self.report['option']['option_strength'], mode='a', title='Option Strength') + \
        self.html(self.report['option']['option_chip'], index=False, mode='a', title='Option Chip')
        return output