import numpy as np
from plotly.offline import plot
import plotly.graph_objs as go
from definitions import max_array_size


def main():
	plot_max_array_size()


def plot_max_array_size():
    logM = np.linspace(3, 16, 13*10+1)
    M = np.floor(2 ** logM)
    logMticks = np.linspace(3, 16, 13+1)
    Mticks = np.floor(2 ** logMticks)
    
    y1 = map(max_array_size, M)
    y2 = M/np.log2(M)


    data = [
        {'x': logM, 'y': np.log2(y1), 'name': 'ArrayMaxSize'},
        {'x': logM, 'y': np.log2(y2), 'name': 'M/logM'}
    ]

    ytick = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000]
    yticklog = np.log2(ytick)

    layout = {
        'title': 'ArrayMaxSize vs M (log-log)', 
        'xaxis': {'title': 'M', 'ticktext': map(str, Mticks), 'tickvals': logMticks},
        'yaxis': {'ticktext': map(str, ytick), 'tickvals': yticklog}
    }

    fig = go.Figure(data=data, layout=layout)
    plot(fig)


main()