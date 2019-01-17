import numpy as np
from plotly.offline import plot
import plotly.graph_objs as go
import pickle
from plot import get_bound_traces

def main():
    # plot_surface_combined(65536, 128, mode='heatmap')
    plot_surface_combined(65536, 128, mode='surface')


def plot_surface_combined(M, w, mode='heatmap'):
    MA, MR = M/16, M/32

    fname = 'data/bitmaps-%s-%s-truncate' % (M, w)
    with open(fname, 'r') as f:
        bitmap_data = pickle.load(f)

    fname = 'data/multigrid-%s-%s-truncate-%s.pickle' % (M, w, M)
    with open(fname, 'r') as f:
        other_data = pickle.load(f)
    other_data['array'][other_data['array'] < 0] = 0
    other_data['runs'][other_data['runs'] < 0] = 0
    other_data['iarray_runs'][other_data['iarray_runs'] < 0] = 0
    other_data['iarray_bitmap'][other_data['iarray_bitmap'] < 0] = 0

    x = range(0, M-1, w)
    y = range(0, M/2+1, w)
    z = np.zeros((M/(2*w)+1, M/w+1))
    z[16:256, 32:512] = bitmap_data['bitmap']
    z[0:32, 0:32] += other_data['array']
    z[0:16, 480:512] += other_data['iarray_runs']
    z[16:32, 480:496] += other_data['iarray_bitmap']
    #z[0:16, 0:512] += other_data['runs']
    # assigning directly double counts...
    for n in range(0, 16):
        for m in range(0, 512):
            if z[n, m] <= 0:
                z[n, m] = other_data['runs'][n, m]
    z[z==0] = -np.inf

    if mode == 'surface':
        traces = [go.Surface(z=z, x=x, y=y, colorscale='Greys')]
        curves = get_bound_traces(M, MA)
        for c in curves:
            # import ipdb; ipdb.set_trace()
            # TODO plot 3d curves as well
            pass
    elif mode == 'heatmap':
        traces = [go.Heatmap(z=z, x=x, y=y, colorscale='Viridis')]
        traces += get_bound_traces(M, MA)

    # full scale ticks
    xticks = range(0, M+1, M/8)
    yticks = range(0, M/2+1, M/(2*8))

    layout = go.Layout(
        showlegend=False,
        title='Container space set density, M=%d (log scale)' % (M),
        xaxis={'title': 'N (cardinality)'},
        yaxis={'title': 'N<sub>R</sub> (runCount)'},
        scene={
            'xaxis': {'title': 'Cardinality', 'tickvals': xticks, 'ticktext': map(str, xticks)},
            'yaxis': {'title': 'RunCount', 'tickvals': yticks, 'ticktext': map(str, yticks)},
            'zaxis': {'title': 'Log F'},
            # TODO html in surf plot - seems to be impossible
        },
    )
    fig = go.Figure(data=traces, layout=layout)
    plot(fig, filename='figures/container-surface-65536.html')


main()