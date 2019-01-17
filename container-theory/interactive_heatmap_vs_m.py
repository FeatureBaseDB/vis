import numpy as np
from plotly.offline import plot
import plotly.graph_objs as go
import pickle
from compute import sum_F_over_rectangle#from conditions import *
from plot import get_bound_traces


def main():
    # compute_and_save_grids()
    # plot_single_heatmap(1024)
    plot_heatmap_slider()


def plot_heatmap_slider():
    data = []
    sets = get_grid_sets()
    for M, width in sets:
        grid, x, y = load_grid(M, width)
        x = np.linspace(0, 1, len(x))
        y = np.linspace(0, 0.5, len(y))
        log_grid = np.log10(grid)
        data.append(go.Heatmap(z=log_grid, x=x, y=y, colorscale='Viridis', visible=False, name='%d bits' % M))

    active = 100
    data[active]['visible'] = True

    annotations = get_bound_traces(1.0, 1/16., normalized=True)
    data += annotations
    alen = len(annotations)

    steps = []
    for i in range(len(data)-alen):
        step = dict(
            label='%s' % sets[i][0],
            method='restyle',
            args=['visible', [False]*(len(data)-alen) + [True]*alen],
        )
        step['args'][1][i] = True
        steps.append(step)

    sliders = [dict(
        active=active,
        currentvalue={'prefix': 'bits: '},
        pad={'t': 50},
        steps=steps
    )]

    layout = go.Layout(
        sliders=sliders,
        showlegend=False,
        title='container space set density (log10 scale)<br>M in [8, 1024]',
        xaxis={'title': 'normalized cardinality'},
        yaxis={'title': 'normalized runCount'},
    )
    fig = go.Figure(data=data, layout=layout)
    plot(fig, filename='figures/container-space.html')


def plot_single_heatmap(M):
    # M = 65536
    # ArrayMaxSize, RunMaxSize = 4096, 2048
    # log_grid, x, y = grid_analytical_integral(M, 1024)

    MA, MR = M/16, M/32
    grid, x, y = load_grid(1024, 16)
    log_grid = np.log10(grid)

    z = log_grid
    data = [go.Heatmap(z=z, x=x, y=y, colorscale='Viridis')]
    # data = [go.Surface(z=z, x=x, y=y, colorscale='Viridis')]
    data += get_bound_traces(M, MA)

    layout = go.Layout(
        showlegend=False,
        title='container space set density (linear scale)<br>M=%d' % (M),
        xaxis={'title': 'cardinality', 'range': [0, M+1]},
        yaxis={'title': 'runCount', 'range': [0, M/2+1]},
    )
    fig = go.Figure(data=data, layout=layout)
    plot(fig, filename='figures/container-space.html')


def get_grid_sets():
    sets = []
    for n in range(8, 64+1):
        sets.append((n, 1))

    for n in range(64+2, 128+1, 2):
        sets.append((n, 2))

    for n in range(128+4, 256+1, 4):
        sets.append((n, 4))

    for n in range(256+8, 512+1, 8):
        sets.append((n, 8))

    for n in range(512+16, 1024+1, 16):
        sets.append((n, 16))

    return sets


def compute_and_save_grids():
    sets = get_grid_sets()

    for s in sets:
        print('computing grid for M=%d, cell_size=%d...' % s)
        t0 = time.time()
        compute_and_save_grid(s[0], s[1])
        dif = time.time() - t0
        print('%f sec' % dif)


def get_grid_name(M, cell_size):
    return 'data/interactive/%dbits-%dcell.pickle' % (M, cell_size)


def load_grid(M, cell_size):
    fname = get_grid_name(M, cell_size)
    with open(fname, 'r') as f:
        grid = pickle.load(f)
    cvec = range(0, M+1, cell_size)
    rvec = range(0, M/2+1, cell_size)

    return grid, cvec, rvec


def compute_and_save_grid(M, cell_size):
    grid, x, y = grid_analytical_integral(M, cell_size)
    fname = get_grid_name(M, cell_size)
    with open(fname, 'w') as f:
        pickle.dump(grid, f)


main()
