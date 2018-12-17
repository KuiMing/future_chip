from plotly.offline import plot
import plotly.graph_objs as go
from ..process import FutureAnalysisProcess


class Figure(FutureAnalysisProcess):
    def __init__(self, date, frequency):
        super(Figure, self).__init__(date, frequency)
    
    @property
    def colors(self):
        colors = []
        INCREASING_COLOR = 'red'
        DECREASING_COLOR = 'green'

        for i in range(len(self.data.close)):
            if i != 0:
                if self.data.close[i] > self.data.close[i-1]:
                    colors.append(INCREASING_COLOR)
                else:
                    colors.append(DECREASING_COLOR)
            else:
                colors.append(DECREASING_COLOR)
        return colors