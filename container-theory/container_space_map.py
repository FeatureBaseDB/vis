import numpy as np
import math
from plotly.offline import plot
import plotly.graph_objs as go
from panda import pm, debug
import pickle
from definitions import logF, large_log_sum, max_array_size
from conditions import *
from plot import get_bound_traces


@pm
def main():
    # compute_container_count_vs_cardinality(65536, 128, 8192)
    # plot_container_count_vs_cardinality(65536, 128, 8192)

    # compute_container_count_vs_cardinality(65536, 128, 65536)
    # plot_container_count_vs_cardinality(65536, 128, 65536)

    # compute_container_count_vs_cardinality_bitmaps_only(65536, 128)
    # plot_container_count_vs_cardinality_bitmaps_only(65536, 128)


def plot_container_count_vs_cardinality(M=65536, w=128, xlim=8192):
    fname = 'data/multigrid-%s-%s-truncate-%s.pickle' % (M, w, xlim)
    with open(fname, 'r') as f:
        grid_data = pickle.load(f)
    card_vec = range(0, xlim, w)
    density = [c*1.0/M for c in card_vec]

    array_count_vec = []
    run_count_vec = []
    bitmap_count_vec = []
    for n, c in enumerate(card_vec):
        if n < grid_data['array'].shape[1]:
            col = grid_data['array'][:, n]
            s = large_log_sum_vec(col)
            array_count_vec.append(s)
        else:
            array_count_vec.append(0)

        if n < grid_data['runs'].shape[1]:
            run_count_vec.append(large_log_sum_vec(grid_data['runs'][:, n]))
        else:
            run_count_vec.append(0)

        if 0 <= n-32 < grid_data['bitmap'].shape[1]:
            bitmap_count_vec.append(large_log_sum_vec(grid_data['bitmap'][:, n-32]))
        else:
            bitmap_count_vec.append(0)

    count_traces = [
        go.Scatter(x=card_vec, y=array_count_vec, name='array', line={'color': 'rgb(255,0,0)'}),
        go.Scatter(x=card_vec, y=run_count_vec, name='runs', line={'color': 'rgb(0,255,0)'}),
        go.Scatter(x=card_vec, y=bitmap_count_vec, name='bitmap', line={'color': 'rgb(0,0,255)'}),
    ]

    combined = np.vstack((array_count_vec, run_count_vec, bitmap_count_vec))
    total = np.max(combined, axis=0)
    freq_traces = [
        go.Scatter(x=card_vec, y=array_count_vec-total, name='array', line={'color': 'rgb(255,0,0)'}),
        go.Scatter(x=card_vec, y=run_count_vec-total, name='runs', line={'color': 'rgb(0,255,0)'}),
        go.Scatter(x=card_vec, y=bitmap_count_vec-total, name='bitmap', line={'color': 'rgb(0,0,255)'}),
#        go.Scatter(x=card_vec, y=0*total, name='total', line={'color': 'rgb(0,0,0)'}),
    ]

    layout = go.Layout(
        title='Container type count vs cardinality',
        xaxis={'title': 'Cardinality'},
        yaxis={'title': 'Log10 count'},
    )
    fig = go.Figure(data=count_traces, layout=layout)
    plot(fig, filename='figures/container-count.html')

    layout = go.Layout(
        title='Container type frequency vs cardinality',
        xaxis={'title': 'Cardinality'},
        yaxis={'title': 'Log10 frequency'},
    )
    fig = go.Figure(data=freq_traces, layout=layout)
    plot(fig, filename='figures/container-frequency.html')

    debug()


def compute_container_count_vs_cardinality(M=65536, w=128, xlim=8192):
    # for a given value of M, count the total number of sets that fall into
    # certain regions of container space, subject to a constraint function
    # this is used to iterate over rectangles that include the desired region,
    # and then grid_analytical_logF_conditional further ignores cells in the grid
    # that don't belong to the region.
    #
    # w = 128  # computation is done in cells that are w x w pixels
    # xlim = 8192  # artificial limit to reduce useless computation for runs and bitmaps

    MA, MR = 4096, 2048

    z_array = grid_analytical_logF_conditional(M, range(0, MA, w), range(0, MA, w), w, array_cond())
    z_iarray_runs = grid_analytical_logF_conditional(M, range(M-MA, M, w), range(0, MR, w), w, iarray_runs_cond())
    z_iarray_bitmap = grid_analytical_logF_conditional(M, range(M-MA, M-MR, w), range(MR, MA, w), w, iarray_bitmap_cond())
    z_runs = grid_analytical_logF_conditional(M, range(0, xlim, w), range(0, MR, w), w, runs_cond())
    # z_bitmap = grid_analytical_logF_conditional(M, range(MA, xlim, w), range(MR, M/2, w), w, bitmap_cond())

    fname = 'data/multigrid-%s-%s-truncate-%s.pickle' % (M, w, xlim)
    grids = {
        'array': z_array,
        'runs': z_runs,
        # 'bitmap': z_bitmap,
        'iarray_runs': z_iarray_runs,
        'iarray_bitmap': z_iarray_bitmap,
    }
    with open(fname, 'w') as f:
        pickle.dump(grids, f)
    debug()


def compute_container_count_vs_cardinality_bitmaps_only(M=65536, w=128, xlim=65536):
    # for a given value of M, count the total number of sets that fall into
    # certain regions of container space, subject to a constraint function
    # this is used to iterate over rectangles that include the desired region,
    # and then grid_analytical_logF_conditional further ignores cells in the grid
    # that don't belong to the region.
    #
    # w = 128  # computation is done in cells that are w x w pixels
    # xlim = 8192  # artificial limit to reduce useless computation for runs and bitmaps

    MA, MR = 4096, 2048

    z_bitmap = grid_analytical_logF_conditional(M, range(MA, xlim, w), range(MR, M/2, w), w, bitmap_cond())

    fname = 'data/bitmaps-%s-%s-truncate' % (M, w)
    grids = {
        'bitmap': z_bitmap,
    }
    with open(fname, 'w') as f:
        pickle.dump(grids, f)
    debug()


def plot_container_count_vs_cardinality_bitmaps_only(M=65536, w=128):
    MA, MR = M/16, M/32

    fname = 'data/bitmaps-%s-%s-truncate' % (M, w)

    with open(fname, 'r') as f:
        data = pickle.load(f)

    x = range(MA, M-MA+1, w)
    y = range(MR, M/2+1, w)
    z = data['bitmap']
    # traces = [go.Heatmap(z=z, x=x, y=y, colorscale='Viridis')]
    traces = [go.Surface(z=z, x=x, y=y, colorscale='Viridis')]

    # annotation plots
    line = {'color': 'rgb(0,255,0)'}
    annotations = [
        go.Scatter(x=[0, M/2], y=[0, M/2], line=line),  # left impossible diagonal
        go.Scatter(x=[M/2, M], y=[M/2, 0], line=line),  # right impossible diagonal
        go.Scatter(x=[0, MA], y=[0, MR], line=line),  # array-run
        go.Scatter(x=[MA, MA], y=[MR, MA], line=line),  # array-bitmap
        # go.Scatter(x=[ArrayMaxSize, M-RunMaxSize], y=[RunMaxSize, RunMaxSize], line=line),  # run-bitmap (no iarray)
        go.Scatter(x=[M-MA, M-MA], y=[MR, MA], line=line),  # iarray-bitmap
        go.Scatter(x=[MA, M-MA], y=[MR, MR], line=line),  # run-bitmap (iarray)
        go.Scatter(x=[M, M-MA], y=[0, MR], line=line),  # iarray-run
    ]
    traces += annotations

    layout = go.Layout(
        showlegend=False,
        title='container space set density (log scale)<br>M=%d' % (M),
        xaxis={'title': 'cardinality', 'range': [0, M+1]},
        yaxis={'title': 'runCount', 'range': [0, M/2+1]},
    )
    fig = go.Figure(data=traces, layout=layout)
    plot(fig, filename='figures/container-space-bitmaps.html')


main()


## deprecated
def compute_and_plot_container_count_vs_M(Mvec):
    # for each M in Mvec, compute the total log count of sets in each container region
    z = np.zeros((5, 9))
    for c in range(0, 8+1):
        for r in range(0, 4+1):
            z[r, c] = logF(c, r, 8)

    c_array, c_bitmap, c_runs, c_all = [], [], [], []
    c_iarray, c_bitmap_iarray, c_runs_iarray = [], [], []
    for M in Mvec:
        MA = max_array_size(M)
        z_array = grid_analytical_logF_conditional(M, range(0, MA+1), range(0, MA+1), 1, array_cond_mutex(M, MA))
        z_runs = grid_analytical_logF_conditional(M, range(0, M+1), range(0, MA/2+1), 1, runs_cond_mutex(M, MA))
        z_bitmap = grid_analytical_logF_conditional(M, range(MA, M-MA/2+1), range(MA/2, M/2+1), 1, bitmap_cond_mutex(M, MA))
        z_iarray = grid_analytical_logF_conditional(M, range(M-MA, M+1), range(0, MA+1), 1, iarray_cond_mutex(M, MA))
        z_runs_iarray = grid_analytical_logF_conditional(M, range(0, M+1), range(0, MA/2+1), 1, runs_cond_mutex_iarray(M, MA))
        z_bitmap_iarray = grid_analytical_logF_conditional(M, range(MA, M-MA+1), range(MA/2, M/2+1), 1, bitmap_cond_mutex_iarray(M, MA))
        c_array.append(math.log10(sum(sum(10**z_array))))
        c_runs.append(math.log10(sum(sum(10**z_runs))))
        c_bitmap.append(math.log10(sum(sum(10**z_bitmap))))
        c_iarray.append(math.log10(sum(sum(10**z_iarray))))
        c_runs_iarray.append(math.log10(sum(sum(10**z_runs_iarray))))
        c_bitmap_iarray.append(math.log10(sum(sum(10**z_bitmap_iarray))))
        c_all.append(math.log10(sum(sum(10**z_array)) + sum(sum(10**z_runs)) + sum(sum(10**z_bitmap))))
        debug()

    traces = [
        go.Scatter(x=Mvec, y=c_array, name='array'),
        go.Scatter(x=Mvec, y=c_bitmap, name='bitmap'),
        go.Scatter(x=Mvec, y=c_runs, name='runs'),
        go.Scatter(x=Mvec, y=c_iarray, name='iarray'),
        go.Scatter(x=Mvec, y=c_bitmap_iarray, name='bitmap-iarray'),
        go.Scatter(x=Mvec, y=c_runs_iarray, name='runs-iarray'),
        # go.Scatter(x=Mvec, y=c_all, name='total'),
    ]
    layout = go.Layout(
        title='Container type count vs M',
        xaxis={'title': 'M'},
        yaxis={'title': 'Log Count'},
    )
    fig = go.Figure(data=traces, layout=layout)
    plot(fig, filename='figures/count-vs-m.html')
    debug()


