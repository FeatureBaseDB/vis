import numpy as np
from plotly.offline import plot
import plotly.graph_objs as go
from conditions import *
from plot import get_bound_traces
from definitions import max_array_size


def main():
    plot_conds(512)


def plot_conds(M):
    MA = max_array_size(M)
    z = np.zeros((M/2+1, M+1))
    xvec, yvec = range(M+1), range(M/2+1)
    for y in yvec:
        for x in xvec:
            # z[y, x] = array_cond_mutex(M, MA)(x, y) + 2 * runs_cond_mutex(M, MA)(x, y) + 4 * bitmap_cond_mutex(M, MA)(x, y)
            z[y, x] = array_cond_mutex(M, MA)(x, y) + 2 * runs_cond_mutex_iarray(M, MA)(x, y) + 4 * bitmap_cond_mutex_iarray(M, MA)(x, y) + 8 * iarray_cond_mutex(M, MA)(x, y)

    traces = [go.Heatmap(z=z, x=xvec, y=yvec, colorscale='Viridis')]
    traces += get_bound_traces(M, MA, 'iarray')

    layout = go.Layout(
        showlegend=False,
        title='container space regions indicators',
        xaxis={'title': 'cardinality', 'range': [0, M+1]},
        yaxis={'title': 'runCount', 'range': [0, M/2+1], 'scaleanchor': 'x'},
    )
    fig = go.Figure(data=traces, layout=layout)
    plot(fig, filename='figures/container-indicators.html')


main()